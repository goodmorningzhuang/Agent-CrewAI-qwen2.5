import cv2

def cartoonize_image(input_path, output_path):
    """
    接收 main.py 传来的绝对路径进行处理
    """
    img = cv2.imread(input_path)
    if img is None: return False
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    cv2.imwrite(output_path, cartoon)
    return True