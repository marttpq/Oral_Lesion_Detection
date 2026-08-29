import base64
import sys

def encode():
    try:
        with open('yolov8.pt', 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode('utf-8')
        
        with open('model_b64.py', 'w') as f:
            f.write(f'MODEL_B64 = "{b64}"\n')
        print("Successfully encoded yolov8.pt to model_b64.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    encode()
