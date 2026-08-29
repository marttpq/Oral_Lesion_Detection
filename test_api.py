import urllib.request
import json
from pathlib import Path

def test_endpoint(model_type, text=""):
    url = "http://localhost:8000/api/assess"
    boundary = "----WebKitFormBoundaryTest123"
    
    parts = []
    # modelType field
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"modelType\"\r\n\r\n{model_type}\r\n".encode("utf-8"))
    
    # text field
    if text:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n{text}\r\n".encode("utf-8"))
        
    # image field
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"test.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n".encode("utf-8"))
    with open("static/uploads/test.jpg", "rb") as f:
        parts.append(f.read())
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    
    body = b"".join(parts)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"\n[+] Test {model_type} -> HTTP {resp.status}")
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("Testing YOLO Model...")
    test_endpoint("YOLO")
    
    print("\nTesting DenseNet-BERT Model...")
    test_endpoint("DenseNet-BERT", "ดื่มเครื่องดื่มแอลกอฮอล์ สูบบุหรี่ ปื้นขาว ลิ้น")
