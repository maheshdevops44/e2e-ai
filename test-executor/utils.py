import os
import zipfile
import boto3
import uuid
import shutil
import base64
from boto3.dynamodb.conditions import Attr, Key

def screenshot(page, name):
    screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'screenshots'))
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"[SCREENSHOT] {name}.png")
    page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))

def page_with_video(browser):
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'videos'))
    os.makedirs(video_dir, exist_ok=True)
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    yield page
    page.close()
    context.close()

def highlight(page, selector):
    page.evaluate(
        '''(selector) => {
            const el = document.querySelector(selector);
            if (el) {
                el.style.outline = '3px solid red';
                el.style.transition = 'outline 0.2s';
            }
        }''',
        selector,
    )

def zip_screenshots_and_videos():
    """Zips the screenshots and videos into a single zip file"""
    try:
        # Use same paths as screenshot() and page_with_video() functions
        screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
        os.makedirs(screenshots_dir, exist_ok=True)
        
        videos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
        os.makedirs(videos_dir, exist_ok=True)

        network_logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "network_logs"))
        os.makedirs(network_logs_dir, exist_ok=True)
        
        screenshots = os.listdir(screenshots_dir) if os.path.exists(screenshots_dir) else []
        print(f"[ZIP] Found screenshots: {screenshots}")
        
        videos = os.listdir(videos_dir) if os.path.exists(videos_dir) else []
        print(f"[ZIP] Found videos: {videos}")

        # Collect all network log files from subdirectories
        network_log_files = []
        if os.path.exists(network_logs_dir):
            for root, dirs, files in os.walk(network_logs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    network_log_files.append(file_path)
        print(f"[ZIP] Found network_logs: {[os.path.basename(f) for f in network_log_files]}")
        
        zip_path = os.path.join(os.path.dirname(__file__), "screenshots.zip")
        print(f"[ZIP] Creating zip file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, "w") as zipf:
            files_added = 0
            for screenshot in screenshots:
                screenshot_path = os.path.join(screenshots_dir, screenshot)
                if os.path.isfile(screenshot_path):
                    zipf.write(screenshot_path, os.path.relpath(screenshot_path, os.path.dirname(__file__)))
                    files_added += 1
                    print(f"[ZIP] Added screenshot: {screenshot}")
            for video in videos:
                video_path = os.path.join(videos_dir, video)
                if os.path.isfile(video_path):
                    zipf.write(video_path, os.path.relpath(video_path, os.path.dirname(__file__)))
                    files_added += 1
                    print(f"[ZIP] Added video: {video}")

            for network_log_path in network_log_files:
                if os.path.isfile(network_log_path):
                    zipf.write(network_log_path, os.path.relpath(network_log_path, os.path.dirname(__file__)))
                    files_added += 1
                    print(f"[ZIP] Added network_log: {os.path.basename(network_log_path)}")
            
            # Always create zip even if empty
            if files_added == 0:
                print("[ZIP] No files found, creating empty zip")
                # Add a small info file to ensure zip exists
                zipf.writestr("info.txt", "No screenshots or videos were generated during this test run.")
                    
        print(f"Successfully created zip file: {zip_path}")
        
    except Exception as e:
        print(f"Error creating zip file: {e}")
        raise Exception(f"Failed to zip screenshots and videos: {str(e)}")

def create_screenshots_and_videos():
    """Create the folders if doesn't exist"""
    print("[CREATE] Ensuring screenshots and videos directories exist")
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
    videos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
    network_logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "network_logs"))
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(network_logs_dir, exist_ok=True)

def delete_screenshots_and_videos():
    """Deletes the screenshots and videos"""
    print("[DELETE] Starting cleanup of screenshots and videos")
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
    videos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
    network_logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "network_logs"))
    print(f"[DELETE] Removing screenshots directory: {screenshots_dir}")
    shutil.rmtree(screenshots_dir)

    print(f"[DELETE] Removing videos directory: {videos_dir}")
    shutil.rmtree(videos_dir)
    
    print(f"[DELETE] Removing network_logs directory: {network_logs_dir}")
    shutil.rmtree(network_logs_dir)
    
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots.zip"))
    print(f"[DELETE] Removing zip file: {zip_path}")
    os.remove(zip_path)
    
    print("[DELETE] Cleanup completed successfully")

def upload_to_s3():
    """Uploads the screenshots and videos to S3 and returns the signed url to the zip file"""
    try:
        print("[UPLOAD] Starting S3 upload process")
        s3_bucket = os.environ.get("S3_BUCKET_ID")
        if not s3_bucket:
            raise Exception("S3_BUCKET_ID environment variable is not set")
            
        s3_region = os.environ.get("AWS_REGION", "us-east-1")  # default to us-east-1 if not set
        
        print(f"[UPLOAD] Using S3 bucket: {s3_bucket}, region: {s3_region}")
        s3 = boto3.client("s3", region_name=s3_region)
        
        zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots.zip"))
        
        if not os.path.exists(zip_path):
            raise Exception(f"Zip file does not exist: {zip_path}")
            
        key = f"screenshots-{uuid.uuid4()}.zip"
        
        print(f"[UPLOAD] Uploading {zip_path} to S3 with key: {key}")
        s3.upload_file(zip_path, s3_bucket, key)
        
        print("[UPLOAD] Generating presigned URL")
        signed_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": s3_bucket, "Key": key},
            ExpiresIn=3600, # 1 hour
        )

        # delete screenshots and videos folders after upload
        delete_screenshots_and_videos()
        
        print(f"[UPLOAD] Upload completed successfully. Signed URL generated (expires in 1 hour)")
        return signed_url, key
        
    except Exception as e:
        print(f"[UPLOAD] Error during S3 upload: {e}")
        raise Exception(f"Failed to upload to S3: {str(e)}")

def download_script(chat_id):
    """Download latest test script for a chat from DynamoDB and return decoded content."""
    
    try:
        print(f"[DOWNLOAD_SCRIPT] Starting download for chat ID: {chat_id}")
        
        region = os.environ.get("AWS_REGION", "us-east-1")
        print(f"[DOWNLOAD_SCRIPT] Using AWS region: {region}")
        
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table("test-scripts")

        # Query by chatId (table hash key is id, so get_item won't work)
        print("[DOWNLOAD_SCRIPT] Querying DynamoDB table for matching records")
        items = []
        response = table.query(
            IndexName="chatId-index",
            KeyConditionExpression=Key("chatId").eq(chat_id),
            ProjectionExpression="id, chatId, createdAt, #c",
            ExpressionAttributeNames={"#c": "content"}
        )
        items.extend(response.get("Items", []))
        while "LastEvaluatedKey" in response:
            response = table.query(
                IndexName="chatId-index",
                KeyConditionExpression=Key("chatId").eq(chat_id),
                ProjectionExpression="id, chatId, createdAt, #c",
                ExpressionAttributeNames={"#c": "content"},
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

        print(f"[DOWNLOAD_SCRIPT] Found {len(items)} matching records")
        
        if not items:
            print("[DOWNLOAD_SCRIPT] No scripts found for the given chat ID")
            return None

        # Choose the most recent by createdAt (ISO string)
        latest = max(items, key=lambda x: x.get("createdAt", ""))
        print(f"[DOWNLOAD_SCRIPT] Selected most recent script: ID={latest.get('id')}, created={latest.get('createdAt')}")
        
        content_b64 = latest.get("content", "")
        try:
            decoded_content = base64.b64decode(content_b64).decode("utf-8") if content_b64 else None
            print(f"[DOWNLOAD_SCRIPT] Successfully decoded script content ({len(decoded_content) if decoded_content else 0} characters)")
            print(decoded_content)
            return decoded_content
        except Exception as e:
            print(f"[DOWNLOAD_SCRIPT] Failed to decode base64 content, returning as-is. Error: {e}")
            # If it's somehow not base64, return as-is
            return content_b64 or None
            
    except Exception as e:
        print(f"[DOWNLOAD_SCRIPT] Error downloading script: {e}")
        raise Exception(f"Failed to download script for chat_id {chat_id}: {str(e)}")

def save_test_results(chat_id, test_results, artifacts):
    """Save the test results to the database"""

    try:
        print(f"[SAVE_TEST_RESULTS] Saving test results for chat ID: {chat_id}")
        print(f"[SAVE_TEST_RESULTS] Test results: {test_results}")

        region = os.environ.get("AWS_REGION", "us-east-1")
        print(f"[SAVE_TEST_RESULTS] Using AWS region: {region}")

        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table("test-scripts")

        # Query by chatId using GSI (assumes GSI exists on chatId)
        print("[SAVE_TEST_RESULTS] Querying DynamoDB table by chatId")
        response = table.query(
            IndexName="chatId-index",  # GSI name
            KeyConditionExpression=Key("chatId").eq(chat_id),
            ProjectionExpression="id, chatId"
        )
        items = response.get("Items", [])
        
        if not items:
            print(f"[SAVE_TEST_RESULTS] No test script found for chat_id: {chat_id}")
            raise Exception(f"No test script found for chat_id: {chat_id}")
        
        # Use the most recent record if multiple exist
        if len(items) > 1:
            print(f"[SAVE_TEST_RESULTS] Multiple records found, using the first one")
        
        record_id = items[0]["id"]
        print(f"[SAVE_TEST_RESULTS] Found record with id: {record_id}")

        # Now update using the correct primary key
        table.update_item(
            Key={"id": record_id}, 
            UpdateExpression="set testResults = :test_results, artifacts = :artifacts", 
            ExpressionAttributeValues={
                ":test_results": test_results, 
                ":artifacts": artifacts
            }
        )
        
        print(f"[SAVE_TEST_RESULTS] Successfully updated test results for id: {record_id}")

    except Exception as e:
        print(f"[SAVE_TEST_RESULTS] Error saving test results: {e}")
        raise Exception(f"Failed to save test results for chat_id {chat_id}: {str(e)}")

def run_tests_in_background(chat_id):
    """Run the complete test execution workflow in the background"""
    import subprocess
    import threading
    
    def execute_tests():
        try:
            print(f"[BACKGROUND] Starting background test execution for chat_id: {chat_id}")
            
            # Download script from DB
            if os.environ.get('ENV') != "local":
                print(f"[BACKGROUND] Downloading test script for chat_id: {chat_id}")
                content = download_script(chat_id)
                
                if content is None:
                    print(f"[BACKGROUND] No test script found for chat_id: {chat_id}")
                    return

                # save file to tests/test_script.py
                try:
                    with open("tests/test_script.py", "w") as f:
                        f.write(content)
                    print("[BACKGROUND] Test script saved")
                except Exception as e:
                    print(f"[BACKGROUND] Failed to save test script: {str(e)}")
                    return

            # run the tests
            print("[BACKGROUND] Starting pytest execution")
            try:
                result = subprocess.run(["pytest", "-s","-x"], capture_output=True, text=True)
                print("[BACKGROUND] Tests completed")
            except Exception as e:
                print(f"[BACKGROUND] Failed to execute pytest: {str(e)}")
                return

            # zip screenshots and videos
            print("[BACKGROUND] Zipping screenshots and videos")
            try:
                zip_screenshots_and_videos()
                print("[BACKGROUND] Zipping completed")
            except Exception as e:
                print(f"[BACKGROUND] Failed to zip screenshots and videos: {str(e)}")
                return

            # upload screenshots and videos to S3
            signed_url = None
            key = None

            print("[BACKGROUND] Uploading screenshots and videos to S3")
            try:
                signed_url, key = upload_to_s3()
                print("[BACKGROUND] S3 upload completed", signed_url, key)
            except Exception as e:
                print(f"[BACKGROUND] Failed to upload to S3: {str(e)}")
                return

            # Save test results to database
            test_results = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "signed_url": signed_url,
                "key": key,
                "status": "completed"
            }
            
            try:
                save_test_results(chat_id, test_results, key)
                print(f"[BACKGROUND] Test results saved for chat_id: {chat_id}")
            except Exception as e:
                print(f"[BACKGROUND] Failed to save test results: {str(e)}")
            
            print(f"[BACKGROUND] Background execution completed for chat_id: {chat_id}")
            
        except Exception as e:
            print(f"[BACKGROUND] Unexpected error in background execution: {str(e)}")
            # Save error status to database
            try:
                error_results = {
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "signed_url": None,
                    "status": "error"
                }
                save_test_results(chat_id, error_results, None)
            except Exception as save_error:
                print(f"[BACKGROUND] Failed to save error results: {str(save_error)}")
    
    # Start the background thread
    thread = threading.Thread(target=execute_tests, daemon=True)
    thread.start()
    print(f"[BACKGROUND] Started background thread for chat_id: {chat_id}")
    return True

