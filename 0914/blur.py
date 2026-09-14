
import cv2

src = cv2.imread("my_input.jpg", cv2.IMREAD_COLOR)

# Kernel Size를 변경해 보기
# borderType을 변경해 보기 (cv2.BORDER_REFLECT)
dst = cv2.blur(src, (9, 9), anchor=(-1, -1), borderType=cv2.BORDER_DEFAULT)

cv2.imshow("dst", dst)
cv2.waitKey()
cv2.destroyAllWindows()