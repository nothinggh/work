# LAPLACIAN 변환을 적용해 보기
# Canny Edge Detection을 적용해 보기

import cv2

src = cv2.imread("Image/wheat.jpg", cv2.IMREAD_COLOR)
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, 3)

cv2.imshow("sobel", sobel)
cv2.waitKey()
cv2.destroyAllWindows()
