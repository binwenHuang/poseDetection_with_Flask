import cv2
import mediapipe as mp
import time
import math


max_body = 0

class PoseDetector:

    def __init__(self, mode = False, upBody = False, smooth=True, detectionCon = 0.5, trackCon = 0.5):

        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        #print(results.pose_landmarks)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def getPosition(self, img, draw=True):
        lmList= []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                #print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 4, (255, 0, 0), cv2.FILLED)
        return lmList


#计算各个关键位置的夹角
def angle(v1, v2):
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180 / math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180 / math.pi)
    # print(angle2)
    if angle1 * angle2 >= 0:
        included_angle = abs(angle1 - angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    return included_angle


def main(file):
    global a,max_body, ang_list,ang_hit
    ang_hit = []
    if file == "" :
        pass
    else:
        # cap = cv2.VideoCapture('test1.mp4')
        cap = cv2.VideoCapture(file)
        # cap = cv2.VideoCapture(0)
        pTime = 0
        detector = PoseDetector()
        try:
            while True:
                success, img = cap.read()
                img = detector.findPose(img)
                lmList = detector.getPosition(img)

                # 右手肘到右肩
                right_elbow2shoulder = [lmList[14][1], lmList[14][2], lmList[12][1], lmList[12][2]]
                # 右手肘到右手腕
                right_elbow2wrist = [lmList[14][1], lmList[14][2], lmList[16][1], lmList[16][2]]
                ang_right_hand = angle(right_elbow2shoulder, right_elbow2wrist)
                #print("右手臂的夹角" + str(ang_right_hand))
                # 判断是否大于120，标准姿态拟定为大于120

                # 右膝盖到右腰
                right_knee2hip = [lmList[26][1], lmList[26][2], lmList[24][1], lmList[24][2]]
                # 右膝盖到右脚踝
                right_knee2ankle = [lmList[26][1], lmList[26][2], lmList[28][1], lmList[28][2]]
                ang_right_leg = angle(right_knee2hip, right_knee2ankle)
                #print("右腿的夹角" + str(ang_right_leg))
                # 判断是否大于140，标准姿态拟定为大于140

                # 左膝盖到左腰
                left_knee2hip = [lmList[25][1], lmList[25][2], lmList[23][1], lmList[23][2]]
                # 左膝盖到左脚踝
                left_knee2ankle = [lmList[25][1], lmList[25][2], lmList[27][1], lmList[27][2]]
                ang_left_leg = angle(left_knee2hip, left_knee2ankle)
                #print("左腿的夹角" + str(ang_left_leg))
                # 判断是否大于150或小于130，标准姿态拟定为大于130~150

                #上身梯形面积
                S1 = lmList[12][1]*lmList[11][2] + lmList[11][1]*lmList[23][2]\
                     + lmList[23][1]*lmList[24][2] + lmList[24][1]*lmList[12][2]

                S2 = lmList[12][1]*lmList[24][2] + lmList[11][1]*lmList[11][2]\
                     + lmList[23][1]*lmList[11][2] + lmList[24][1]*lmList[23][2]
                S = abs(S1-S2)
                # print(S)

                #引拍动作分析
                if S > max_body:
                    max_body = S
                    ang_list = [ang_right_hand,ang_right_leg,ang_left_leg]


                #计算击球时右手臂的夹角
                #同右手肘x坐标为起点的水平向量
                level_vector = [lmList[14][1], lmList[14][2], lmList[14][1] + 10, lmList[14][2]]
                if lmList[16][2] > lmList[14][2]:
                    ang_hit_hand = angle(level_vector, right_elbow2wrist)
                    if 25 > ang_hit_hand > 15:
                        ang_hit.append([ang_right_hand,ang_right_leg,ang_left_leg])

                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime

                cv2.putText(img, str(int(fps)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                ret, jpeg = cv2.imencode('.jpg', img)
                img_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n\r\n')

                cv2.imshow("Image", img)
                if cv2.waitKey(1) == ord("q"):
                    break
        except:
            pass

        print("引拍：右手臂的夹角" + str(ang_list[0]) + " 右腿的夹角" + str(ang_list[1]) +" 左腿的夹角" + str(ang_list[2]))
        print("击球：右手臂的夹角" + str(ang_hit[0][0]) + " 右腿的夹角" + str(ang_hit[0][1]) +" 左腿的夹角" + str(ang_hit[0][2]))

        #引拍：
        #判断引拍手臂动作
        if ang_list[0] < 140 :
            print("引拍：手臂伸展角度过小，影响拍面位置调整")
        elif ang_list[0] > 170:
            print("引拍：手臂伸展角度过大，影响球拍稳定性")
        else:
            print("引拍：手臂标准")
        #判断引拍右腿动作
        if 170 < ang_list[1]:
            print("引拍：右腿过度伸展，影响挥拍稳定性")
        elif ang_list[1] < 140:
            print("引拍：右腿角度过小，影响身体平衡")
        else:
            print("引拍：右腿标准")
        #判断引拍左腿动作
        if 170 < ang_list[2]:
            print("引拍：重心过高，影响挥拍稳定与自身平衡")
        elif ang_list[2] < 140:
            print("引拍：左腿过度弯曲，影响身体稳定性")
        else:
            print("引拍：左腿标准")

        #击球动作判断
        #击球手臂动作
        if ang_list[0] < 140 :
            print("击球：手臂伸展角度过小，影响击球力度")
        elif ang_list[0] > 170:
            print("击球：手臂伸展角度过大，影响击球准确性")
        else:
            print("击球：手臂标准")
        #判断击球右腿动作
        if 170 < ang_list[1]:
            print("击球：右腿过度伸展，影响击球稳定性与击球力度")
        elif ang_list[1] < 140:
            print("击球：右腿角度过小，影响击球力度与身体平衡")
        else:
            print("击球：右腿标准")
        #判断击球左腿动作
        if 170 < ang_list[2]:
            print("击球：重心过低，影响击球稳定与自身平衡")
        elif ang_list[2] < 140:
            print("击球：左腿过度弯曲，影响击球稳定与自身平衡")
        else:
            print("击球：左腿标准")


main("test1.mp4")
