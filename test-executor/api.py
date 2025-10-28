import subprocess
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
from utils import zip_screenshots_and_videos, upload_to_s3, download_script, run_tests_in_background, save_test_results, delete_screenshots_and_videos
import requests
import os
import base64
import json
from dotenv import load_dotenv
import platform
from urllib.parse import urlparse
import uuid
from const import sampleTestFile
import psycopg2
import asyncpg
import time

class TestScript(BaseModel):
    content: str
    createdAt: str
    chatId: str
    id: str

load_dotenv()

def get_db_credentials():
    """Get database credentials from environment variables"""
    try:
        # Get DB info from environment variables (injected by ECS)
        host = os.environ.get('DB_ENDPOINT')
        database = os.environ.get('DB_DATABASE_NAME', 'postgres')
        username = os.environ.get('DB_USERNAME', 'postgres')
        password = os.environ.get('DB_PASSWORD')  # Injected from Secrets Manager by ECS
        port = os.environ.get('DB_PORT', '5432')

        if not host:
            return None, "DB_ENDPOINT environment variable not set"

        if not password:
            return None, "DB_PASSWORD environment variable not set"
        
        return {
            'host': host,
            'database': database,
            'username': username,
            'password': password,
            'port': int(port)
        }, None
        
    except Exception as e:
        return None, f"Error getting credentials: {str(e)}"

def test_postgres_connection_sync():
    """Test PostgreSQL connection using psycopg2 (synchronous)"""
    try:
        credentials, error = get_db_credentials()
        if error:
            return {"success": False, "error": error, "connection_type": "sync"}
        
        start_time = time.time()
        
        # Create connection
        conn = psycopg2.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['username'],
            password=credentials['password'],
            port=credentials['port'],
            connect_timeout=10,
            sslmode='require'
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user, now();")
        result = cursor.fetchone()
        
        connection_time = time.time() - start_time
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "connection_type": "sync",
            "connection_time_ms": round(connection_time * 1000, 2),
            "database_info": {
                "version": result[0] if result else None,
                "database": result[1] if result else None,
                "user": result[2] if result else None,
                "timestamp": str(result[3]) if result else None
            },
            "credentials_info": {
                "host": credentials['host'],
                "database": credentials['database'],
                "username": credentials['username'],
                "port": credentials['port']
            }
        }
        
    except psycopg2.Error as e:
        return {
            "success": False,
            "error": f"PostgreSQL error: {str(e)}",
            "connection_type": "sync"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}",
            "connection_type": "sync"
        }

async def test_postgres_connection_async():
    """Test PostgreSQL connection using asyncpg (asynchronous)"""
    try:
        credentials, error = get_db_credentials()
        if error:
            return {"success": False, "error": error, "connection_type": "async"}
        
        start_time = time.time()
        
        # Create connection
        conn = await asyncpg.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['username'],
            password=credentials['password'],
            port=credentials['port'],
            command_timeout=10,
            ssl=True
        )
        
        # Test query
        result = await conn.fetchrow("SELECT version(), current_database(), current_user, now();")
        
        connection_time = time.time() - start_time
        
        await conn.close()
        
        return {
            "success": True,
            "connection_type": "async",
            "connection_time_ms": round(connection_time * 1000, 2),
            "database_info": {
                "version": result[0] if result else None,
                "database": result[1] if result else None,
                "user": result[2] if result else None,
                "timestamp": str(result[3]) if result else None
            },
            "credentials_info": {
                "host": credentials['host'],
                "database": credentials['database'],
                "username": credentials['username'],
                "port": credentials['port']
            }
        }
        
    except asyncpg.PostgresError as e:
        return {
            "success": False,
            "error": f"AsyncPG PostgreSQL error: {str(e)}",
            "connection_type": "async"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Async connection error: {str(e)}",
            "connection_type": "async"
        }

def perform_traceroute(target_url, max_hops=30, timeout=5):
    """Perform traceroute to a target URL and return the results"""
    try:
        # Extract hostname from URL
        parsed_url = urlparse(target_url)
        hostname = parsed_url.hostname or parsed_url.netloc
        
        if not hostname:
            return {"error": "Could not extract hostname from URL"}
        
        # Determine the correct traceroute command based on OS
        if platform.system().lower() == "windows":
            cmd = ["tracert", "-h", str(max_hops), "-w", str(timeout * 1000), hostname]
        else:
            cmd = ["traceroute", "-m", str(max_hops), "-w", str(timeout), hostname]
        
        # Run traceroute command
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60  # Overall timeout for the command
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "hops": parse_traceroute_output(result.stdout, platform.system().lower())
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "Traceroute command failed",
                "output": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Traceroute command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "Traceroute command not found on system"}
    except Exception as e:
        return {"success": False, "error": f"Traceroute failed: {str(e)}"}

def parse_traceroute_output(output, os_type):
    """Parse traceroute output to extract hop information"""
    hops = []
    lines = output.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if os_type == "windows":
            # Windows tracert format: "  1     1 ms     1 ms     1 ms  192.168.1.1"
            if line and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 2:
                    hop_num = parts[0]
                    # Look for IP address (last part that looks like an IP or hostname)
                    ip_or_host = parts[-1] if parts[-1] != "ms" else parts[-2] if len(parts) > 1 else "Unknown"
                    # Extract timing info
                    timing = [p for p in parts[1:-1] if p != "ms"]
                    hops.append({
                        "hop": int(hop_num),
                        "host": ip_or_host,
                        "timings": timing[:3] if len(timing) >= 3 else timing
                    })
        else:
            # Unix traceroute format: " 1  gateway (192.168.1.1)  0.123 ms  0.456 ms  0.789 ms"
            if line and line.split()[0].isdigit():
                parts = line.split()
                hop_num = parts[0]
                # Find host/IP (usually in parentheses or second element)
                host = "Unknown"
                for part in parts[1:]:
                    if '(' in part and ')' in part:
                        host = part.strip('()')
                        break
                    elif not part.endswith('ms') and '.' in part:
                        host = part
                        break
                
                # Extract timings
                timings = [p.replace('ms', '') for p in parts if p.endswith('ms')]
                hops.append({
                    "hop": int(hop_num),
                    "host": host,
                    "timings": timings[:3]
                })
    
    return hops

def perform_curl(target_url, timeout=10):
    """Perform curl to a target URL and return the results with timing information"""
    try:
        # Build curl command with verbose output and timing
        cmd = [
            "curl",
            "-w", "@-",  # Write format from stdin
            "-s",        # Silent mode
            "-S",        # Show errors
            "--max-time", str(timeout),
            "--insecure",  # Skip SSL verification (like verify=False in requests)
            target_url
        ]
        
        # Custom format string for detailed timing information
        format_string = """{
    "time_namelookup": %{time_namelookup},
    "time_connect": %{time_connect},
    "time_appconnect": %{time_appconnect},
    "time_pretransfer": %{time_pretransfer},
    "time_redirect": %{time_redirect},
    "time_starttransfer": %{time_starttransfer},
    "time_total": %{time_total},
    "speed_download": %{speed_download},
    "speed_upload": %{speed_upload},
    "size_download": %{size_download},
    "size_upload": %{size_upload},
    "size_header": %{size_header},
    "size_request": %{size_request},
    "http_code": %{http_code},
    "http_connect": %{http_connect},
    "num_connects": %{num_connects},
    "num_redirects": %{num_redirects},
    "remote_ip": "%{remote_ip}",
    "remote_port": %{remote_port},
    "local_ip": "%{local_ip}",
    "local_port": %{local_port}
}"""
        
        # Run curl command with format string
        result = subprocess.run(
            cmd,
            input=format_string,
            capture_output=True,
            text=True,
            timeout=timeout + 5  # Overall timeout slightly longer than curl timeout
        )
        
        if result.returncode == 0:
            try:
                # Parse the JSON output from curl
                timing_data = json.loads(result.stdout)
                return {
                    "success": True,
                    "timing": timing_data,
                    "total_time_ms": timing_data.get("time_total", 0) * 1000,
                    "dns_time_ms": timing_data.get("time_namelookup", 0) * 1000,
                    "connect_time_ms": timing_data.get("time_connect", 0) * 1000,
                    "ssl_time_ms": (timing_data.get("time_appconnect", 0) - timing_data.get("time_connect", 0)) * 1000 if timing_data.get("time_appconnect", 0) > 0 else 0,
                    "transfer_time_ms": (timing_data.get("time_starttransfer", 0) - timing_data.get("time_pretransfer", 0)) * 1000,
                    "http_code": timing_data.get("http_code", 0),
                    "remote_ip": timing_data.get("remote_ip", ""),
                    "download_speed_bytes_per_sec": timing_data.get("speed_download", 0),
                    "size_download_bytes": timing_data.get("size_download", 0)
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "raw_output": result.stdout,
                    "note": "Could not parse timing data as JSON"
                }
        else:
            return {
                "success": False,
                "error": result.stderr or "Curl command failed",
                "returncode": result.returncode,
                "raw_output": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Curl command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "Curl command not found on system"}
    except Exception as e:
        return {"success": False, "error": f"Curl failed: {str(e)}"}

async def merge_async_iterators(*iterators):
    """Merge multiple async iterators and yield items as they become available."""
    async def get_next(it):
        try:
            return await it.__anext__()
        except StopAsyncIteration:
            return None
    
    pending = {asyncio.create_task(get_next(it)): it for it in iterators}
    
    while pending:
        done, _ = await asyncio.wait(pending.keys(), return_when=asyncio.FIRST_COMPLETED)
        
        for task in done:
            iterator = pending.pop(task)
            result = task.result()
            if result is not None:
                yield result
                # Schedule the next item from this iterator
                pending[asyncio.create_task(get_next(iterator))] = iterator

app = FastAPI()

def log_request_source(request: Request, endpoint_name: str = "unknown"):
    """Log request source information for debugging/monitoring"""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:50]
    forwarded_for = request.headers.get("x-forwarded-for", "none")
    referer = request.headers.get("referer", "none")

    print(f"[{endpoint_name}] Request from IP: {client_ip} | UA: {user_agent} | Forwarded: {forwarded_for} | Referer: {referer}")

    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "forwarded_for": forwarded_for,
        "referer": referer
    }

@app.get("/")
async def root(request: Request):
    # Log and get request source info
    request_info = log_request_source(request, "root")

    print("--------------------------------")
    print({
        "message": "Hello World",
        "request_info": {
            **request_info,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
    })
    print("--------------------------------")

    return {
        "message": "Hello World",
        "request_info": {
            **request_info,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test-postgres")
async def test_postgres_connection():
    """Test PostgreSQL connection with both sync and async clients"""
    
    # Log request details
    print("Testing PostgreSQL database connection...")
    
    results = {}
    
    # Test synchronous connection
    print("Testing synchronous psycopg2 connection...")
    sync_result = test_postgres_connection_sync()
    results["sync_connection"] = sync_result
    
    # Test asynchronous connection
    print("Testing asynchronous asyncpg connection...")
    async_result = await test_postgres_connection_async()
    results["async_connection"] = async_result
    
    # Determine overall status
    overall_success = sync_result.get("success", False) or async_result.get("success", False)
    
    print(f"PostgreSQL connection test completed. Success: {overall_success}")
    
    return {
        "overall_success": overall_success,
        "timestamp": time.time(),
        "results": results,
        "environment_variables": {
            "DB_ENDPOINT": os.environ.get('DB_ENDPOINT', 'NOT_SET'),
            "DB_DATABASE_NAME": os.environ.get('DB_DATABASE_NAME', 'NOT_SET'),
            "DB_USERNAME": os.environ.get('DB_USERNAME', 'NOT_SET'),
            "DB_PASSWORD": "SET" if os.environ.get('DB_PASSWORD') else "NOT_SET",
            "DB_PORT": os.environ.get('DB_PORT', 'NOT_SET'),
            "AWS_REGION": os.environ.get('AWS_REGION', 'NOT_SET')
        }
    }

@app.get("/ping-target")
def ping_target(include_traceroute: bool = False, include_curl: bool = False):
    """Ping all the targets and return the results with optional traceroute and curl"""

    targets = [
        "https://www.google.com",
        "https://clearance-qa.express-scripts.com/spclr",
        "https://sprxp-qa.express-scripts.com/sprxp",
        "https://spcia-qa.express-scripts.com/spcia",
        "https://spcrmqa-internal.express-scripts.com/spcrm88",
    ]

    results = []
    for target in targets:
        result_entry = {"target": target}
        
        # Perform HTTP ping
        try:
            response = requests.get(target, timeout=10, verify=False)
            if response.status_code == 200:
                result_entry.update({
                    "status": "ok",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "html_response": response.text
                })
            else:
                result_entry.update({
                    "status": "failed",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "html_response": response.text
                })
        except Exception as e:
            result_entry.update({
                "status": "failed",
                "error": str(e)
            })
        
        # Perform traceroute if requested
        if include_traceroute:
            print(f"Performing traceroute to {target}...")
            traceroute_result = perform_traceroute(target)
            result_entry["traceroute"] = traceroute_result
        
        # Perform curl if requested
        if include_curl:
            print(f"Performing curl to {target}...")
            curl_result = perform_curl(target)
            result_entry["curl"] = curl_result
        
        results.append(result_entry)

    return {"status": "ok", "results": results}

@app.get("/test-playwright-connectivity")
def test_playwright_connectivity():
    """Test connectivity using Playwright-like approach to identify timeout causes"""
    import socket
    import ssl
    import time

    targets = [
        "https://www.google.com",  # This works according to user
        "https://clearance-qa.express-scripts.com/spclr",
        "https://sprxp-qa.express-scripts.com/sprxp",
        "https://spcia-qa.express-scripts.com/spcia",
        "https://spcrmqa-internal.express-scripts.com/spcrm88",
    ]

    results = []
    for target in targets:
        result_entry = {"target": target}

        # Extract hostname and port
        from urllib.parse import urlparse
        parsed = urlparse(target)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)

        # Test 1: DNS resolution
        dns_start = time.time()
        try:
            ip_address = socket.gethostbyname(hostname)
            dns_time = time.time() - dns_start
            result_entry["dns_resolution"] = {
                "success": True,
                "ip": ip_address,
                "time_ms": dns_time * 1000
            }
        except Exception as e:
            result_entry["dns_resolution"] = {
                "success": False,
                "error": str(e)
            }
            results.append(result_entry)
            continue

        # Test 2: TCP connection (similar to browser)
        tcp_start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10 second timeout like requests
            sock.connect((ip_address, port))
            tcp_time = time.time() - tcp_start
            result_entry["tcp_connection"] = {
                "success": True,
                "time_ms": tcp_time * 1000
            }
            sock.close()
        except Exception as e:
            result_entry["tcp_connection"] = {
                "success": False,
                "error": str(e)
            }

        # Test 3: SSL handshake (for HTTPS)
        if parsed.scheme == 'https':
            ssl_start = time.time()
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((ip_address, port))

                ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
                ssl_time = time.time() - ssl_start
                result_entry["ssl_handshake"] = {
                    "success": True,
                    "time_ms": ssl_time * 1000,
                    "cipher": ssl_sock.cipher()[0] if ssl_sock.cipher() else None
                }
                ssl_sock.close()
            except Exception as e:
                result_entry["ssl_handshake"] = {
                    "success": False,
                    "error": str(e)
                }

        # Test 4: HTTP HEAD request (minimal request like browser preflight)
        head_start = time.time()
        try:
            response = requests.head(target, timeout=10, verify=False, allow_redirects=True)
            head_time = time.time() - head_start
            result_entry["head_request"] = {
                "success": True,
                "status_code": response.status_code,
                "time_ms": head_time * 1000,
                "final_url": response.url
            }
        except Exception as e:
            result_entry["head_request"] = {
                "success": False,
                "error": str(e)
            }

        results.append(result_entry)

    return {"status": "ok", "results": results}

# Takes a chat id and runs the tests
@app.get("/run-tests/{chat_id}")
async def run_tests(chat_id: str):
    """Run pytest and return stdout/stderr and exit code as JSON."""

    try:
        # Download script from DB
        if os.environ['ENV'] != "local":
            print(f"Downloading test script for chat_id: {chat_id}")
            content = download_script(chat_id)
            
            if content is None:
                raise HTTPException(status_code=404, detail=f"No test script found for chat_id: {chat_id}")

            # save file to tests/test_script.py
            try:
                with open("tests/test_script.py", "w") as f:
                    f.write(content)
                print("Test script saved")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save test script: {str(e)}")

        # run the tests
        print("Starting pytest execution")
        try:
            result = subprocess.run(["pytest", "-s","-x"], capture_output=True, text=True)
            print("Tests done")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to execute pytest: {str(e)}")

        # zip screenshots and videos, run after the tests are done
        print("Zipping screenshots and videos")
        try:
            zip_screenshots_and_videos()
            print("Zipping screenshots and videos done")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to zip screenshots and videos: {str(e)}")

        # upload screenshots and videos to S3
        if os.environ['ENV'] != "local":
            print("Uploading screenshots and videos to S3")
            try:
                signed_url = upload_to_s3()
                print("Uploading screenshots and videos to S3 done")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
        else:
            signed_url = None
            print("Local environment - skipping S3 upload")

        print(f"Request completed for chat_id: {chat_id}")
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "signed_url": signed_url
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")

@app.get("/run-tests-background/{chat_id}")
async def run_tests_background(chat_id: str):
    """Take the chat_id and run the tests in the background respond to the HTTP request with a 200 status code immediately"""
    
    try:
        print(f"Received background test request for chat_id: {chat_id}")
        
        # Start the background execution
        success = run_tests_in_background(chat_id)
        
        if success:
            print(f"Background execution started successfully for chat_id: {chat_id}")
            return {
                "status": "accepted",
                "message": f"Test execution started in background for chat_id: {chat_id}",
                "chat_id": chat_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start background execution")
            
    except Exception as e:
        print(f"Error starting background execution for chat_id {chat_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start background execution: {str(e)}")


@app.get("/run-tests-stream/{chat_id}")
async def run_tests_stream(chat_id: str):
    """Run pytest and stream stdout/stderr in real-time."""
    
    async def generate():
        # Download script from DB
        if os.environ['ENV'] != "local":
            # save file to tests/test_script.py
            try:
                print(f"Downloading test script for chat_id: {chat_id}")
                
                content = download_script(chat_id)
                
                if content is None:
                    print(f"No test script found for chat_id: {chat_id}")
                    raise HTTPException(status_code=404, detail=f"No test script found for chat_id: {chat_id}")
                
                with open("tests/test_script.py", "w") as f:
                    print(f"Writing test script to tests/test_script.py")
                    f.write(content)

                print("Test script saved")

            except Exception as e:
                print(f"Failed to save test script: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to save test script: {str(e)}")

        # Start the pytest process with unbuffered output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        process = await asyncio.create_subprocess_exec(
            "xvfb-run", "pytest", "-s", "-v", "-x","--tb=short",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        # Stream stdout and stderr concurrently
        stdout_output = []
        stderr_output = []
        
        async def stream_output():
            
            # Task for stdout - read chunks for immediate output
            async def read_stdout():
                buffer = ""
                while True:
                    try:
                        chunk = await process.stdout.read(1024)
                        if not chunk:
                            if buffer:
                                stdout_output.append(buffer)
                                yield {
                                    "type": "stdout",
                                    "data": buffer
                                }
                            break
                        
                        text = chunk.decode('utf-8', errors='ignore')
                        buffer += text
                        
                        # Send complete lines immediately, keep partial line in buffer
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            stdout_output.append(line + '\n')
                            yield {
                                "type": "stdout",
                                "data": line
                            }
                        
                        # Also send buffer if it gets too long (for prints without newlines)
                        if len(buffer) > 100:
                            stdout_output.append(buffer)
                            yield {
                                "type": "stdout",
                                "data": buffer
                            }
                            buffer = ""
                            
                    except Exception:
                        break
            
            # Task for stderr
            async def read_stderr():
                buffer = ""
                while True:
                    try:
                        chunk = await process.stderr.read(1024)
                        if not chunk:
                            if buffer:
                                stderr_output.append(buffer)
                                yield {
                                    "type": "stderr",
                                    "data": buffer
                                }
                            break
                        
                        text = chunk.decode('utf-8', errors='ignore')
                        buffer += text
                        
                        # Send complete lines immediately, keep partial line in buffer
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            stderr_output.append(line + '\n')
                            yield {
                                "type": "stderr",
                                "data": line
                            }
                        
                        # Also send buffer if it gets too long
                        if len(buffer) > 100:
                            stderr_output.append(buffer)
                            yield {
                                "type": "stderr",
                                "data": buffer
                            }
                            buffer = ""
                            
                    except Exception:
                        break
            
            # Merge both streams
            async for chunk in merge_async_iterators(read_stdout(), read_stderr()):
                yield chunk
        
        # Stream output as it comes
        async for chunk in stream_output():
            yield f"data: {json.dumps(chunk)}\n"

        # Wait for process to complete
        await process.wait()
        
        # Send final status
        yield f"data: {json.dumps({'type': 'exit', 'returncode': process.returncode})}\n"
        
        # Zip and upload after completion
        zip_screenshots_and_videos()
        signed_url, key = upload_to_s3()

        # Save test results to database
        test_results = {
            "returncode": process.returncode,
            "stdout": ''.join(stdout_output),
            "stderr": ''.join(stderr_output),
            "signed_url": signed_url,
            "key": key,
            "status": "completed"
        }

        save_test_results(chat_id, test_results, key)

        print(f"Test results for chat_id: {chat_id} - \n \n{test_results}")
            
        yield f"data: {json.dumps({'type': 'complete', 'signed_url': signed_url, 'key': key, 'returncode': process.returncode, 'status': 'completed'})}\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/run-tests-stream-base/{chat_id}")
async def run_tests_stream_base(chat_id: str):
    """Run pytest and return stdout/stderr and exit code as JSON."""

    async def generate():
        import json
        import asyncio
        
        try:
            # Download script from DB - http://localhost:3000/api/test-script/{chat_id}
            if os.environ['ENV'] != "local":
                print(f"Downloading test script for chat_id: {chat_id}")
                content = download_script(chat_id)
                
                if content is None:
                    raise HTTPException(status_code=404, detail=f"No test script found for chat_id: {chat_id}")

                # save file to tests/test_script.py
                try:
                    with open("tests/test_script.py", "w") as f:
                        f.write(content)
                    print("Test script saved")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to save test script: {str(e)}")

            # run the tests
            print("Starting pytest execution")
            
            # Use a threaded approach that works on Windows
            import concurrent.futures
            import threading
            
            def run_pytest_sync():
                result = subprocess.run(["pytest", "-s","-x"], capture_output=True, text=True)
                return result.returncode, result.stdout, result.stderr
            
            # Start pytest in a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_pytest_sync)
                
                # Send processing messages while pytest runs
                while not future.done():
                    yield f"data: {json.dumps({'status': 'processing', 'message': 'Running tests...'})}\n\n"
                    await asyncio.sleep(1.0)  # Wait 1 second between messages
                
                # Get the result
                returncode, stdout, stderr = future.result()
                
                # Create result object like subprocess.run
                class Result:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = stdout
                        self.stderr = stderr
                
                result = Result(returncode, stdout, stderr)
                print("Tests done")

            # zip screenshots and videos, run after the tests are done
            print("Zipping screenshots and videos")
            try:
                zip_screenshots_and_videos()
                print("Zipping screenshots and videos done")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to zip screenshots and videos: {str(e)}")

            # upload screenshots and videos to S3
            if os.environ['ENV'] != "local":
                print("Uploading screenshots and videos to S3")
                try:
                    signed_url = upload_to_s3()
                    print("Uploading screenshots and videos to S3 done")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
            else:
                signed_url = None
                print("Local environment - skipping S3 upload")

            print(f"Request completed for chat_id: {chat_id}")
            
            # Send final result - exact same format as original run-tests endpoint
            final_result = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "signed_url": signed_url
            }
            yield f"data: {json.dumps(final_result)}\n\n"
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Catch any other unexpected errors and return same format as original
            import traceback
            print("Unexpected error occurred: ", traceback.print_exc())
            error_result = {
                "error": f"Unexpected error occurred: {str(e)}"
            }
            yield f"data: {json.dumps(error_result)}\n\n"

    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Transfer-Encoding": "chunked",
        }
    )

@app.get("/run-tests-sample")
async def run_tests_sample():
    """Run the sample test"""
    """Run pytest and stream stdout/stderr in real-time."""
    
    chat_id = str(uuid.uuid4())

    async def generate():
        try:
            print(f"Downloading test script for chat_id: {chat_id}")
            
            content = sampleTestFile
            
            if content is None:
                print(f"No test script found for chat_id: {chat_id}")
                raise HTTPException(status_code=404, detail=f"No test script found for chat_id: {chat_id}")
            
            with open("tests/test_script.py", "w") as f:
                print(f"Writing test script to tests/test_script.py")
                f.write(content)

            print("Test script saved")

        except Exception as e:
            print(f"Failed to save test script: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save test script: {str(e)}")
        
        os.environ["EDBUG"] = "pw:api"

        # Start the pytest process with unbuffered output
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        process = await asyncio.create_subprocess_exec(
            "xvfb-run", "pytest", "-s", "-v", "-x","--tb=short",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        # Stream stdout and stderr concurrently
        stdout_output = []
        stderr_output = []
        
        async def stream_output():
            
            # Task for stdout - read chunks for immediate output
            async def read_stdout():
                buffer = ""
                while True:
                    try:
                        chunk = await process.stdout.read(1024)
                        if not chunk:
                            if buffer:
                                stdout_output.append(buffer)
                                yield {
                                    "type": "stdout",
                                    "data": buffer
                                }
                            break
                        
                        text = chunk.decode('utf-8', errors='ignore')
                        buffer += text
                        
                        # Send complete lines immediately, keep partial line in buffer
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            stdout_output.append(line + '\n')
                            yield {
                                "type": "stdout",
                                "data": line
                            }
                        
                        # Also send buffer if it gets too long (for prints without newlines)
                        if len(buffer) > 100:
                            stdout_output.append(buffer)
                            yield {
                                "type": "stdout",
                                "data": buffer
                            }
                            buffer = ""
                            
                    except Exception:
                        break
            
            # Task for stderr
            async def read_stderr():
                buffer = ""
                while True:
                    try:
                        chunk = await process.stderr.read(1024)
                        if not chunk:
                            if buffer:
                                stderr_output.append(buffer)
                                yield {
                                    "type": "stderr",
                                    "data": buffer
                                }
                            break
                        
                        text = chunk.decode('utf-8', errors='ignore')
                        buffer += text
                        
                        # Send complete lines immediately, keep partial line in buffer
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            stderr_output.append(line + '\n')
                            yield {
                                "type": "stderr",
                                "data": line
                            }
                        
                        # Also send buffer if it gets too long
                        if len(buffer) > 100:
                            stderr_output.append(buffer)
                            yield {
                                "type": "stderr",
                                "data": buffer
                            }
                            buffer = ""
                            
                    except Exception:
                        break
            
            # Merge both streams
            async for chunk in merge_async_iterators(read_stdout(), read_stderr()):
                yield chunk
        
        # Stream output as it comes
        async for chunk in stream_output():
            yield f"data: {json.dumps(chunk)}\n"

        # Wait for process to complete
        await process.wait()
        
        # Send final status
        yield f"data: {json.dumps({'type': 'exit', 'returncode': process.returncode})}\n"

        zip_screenshots_and_videos()

        signed_url, key = upload_to_s3()

        # Save test results to database
        test_results = {
            "returncode": process.returncode,
            "stdout": ''.join(stdout_output),
            "stderr": ''.join(stderr_output),
            "signed_url": signed_url,
            "key": key,
            "status": "completed"
        }

        print(f"Test results: {test_results}")
            
        yield f"data: {json.dumps({'type': 'complete', 'signed_url': signed_url, 'key': key, 'stdout': ''.join(stdout_output), 'stderr': ''.join(stderr_output), 'returncode': process.returncode, 'status': 'completed'})}\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False) 