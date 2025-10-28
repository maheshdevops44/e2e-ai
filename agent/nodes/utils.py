import os
import zipfile
import boto3
import uuid
import shutil

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
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "screenshots"))
    os.makedirs(screenshots_dir, exist_ok=True)
    
    videos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
    os.makedirs(videos_dir, exist_ok=True)
    
    screenshots = os.listdir(screenshots_dir)
    print(screenshots)
    
    videos = os.listdir(videos_dir)
    print(videos)
    
    with zipfile.ZipFile(os.path.join(os.path.dirname(__file__), "screenshots.zip"), "w") as zipf:
        for screenshot in screenshots:
            screenshot_path = os.path.join(screenshots_dir, screenshot)
            if os.path.isfile(screenshot_path):
                zipf.write(screenshot_path, os.path.relpath(screenshot_path, os.path.dirname(__file__)))
        for video in videos:
            video_path = os.path.join(videos_dir, video)
            if os.path.isfile(video_path):
                zipf.write(video_path, os.path.relpath(video_path, os.path.dirname(__file__)))

def delete_screenshots_and_videos():
    """Deletes the screenshots and videos"""
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots"))
    videos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "videos"))
    shutil.rmtree(screenshots_dir)
    shutil.rmtree(videos_dir)
    os.remove(os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots.zip")))

def upload_to_s3():
    """Uploads the screenshots and videos to S3 and returns the signed url to the zip file"""
    s3_bucket = os.environ["S3_BUCKET_ID"]
    s3_region = os.environ.get("AWS_REGION", "us-east-1")  # default to us-east-1 if not set
    s3 = boto3.client("s3", region_name=s3_region)
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "screenshots.zip"))
    key = f"screenshots-{uuid.uuid4()}.zip"
    s3.upload_file(zip_path, s3_bucket, key)
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_bucket, "Key": key},
        ExpiresIn=3600,
    )