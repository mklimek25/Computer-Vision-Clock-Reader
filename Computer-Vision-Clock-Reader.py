import cv2
import imutils
import math
import tkinter

class clock_reader(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.image = self.cap.read()[1]
        self.center = (int(self.image.shape[1]/2), int(self.image.shape[0]/2))
        self.bsp = 425  # box size parameter
        self.cut_center = (self.bsp,self.bsp)

    def distance_from_center(self, list_chain):
        x_value = list_chain[0][0]
        y_value = list_chain[0][1]
        x_center = self.bsp
        y_center = self.bsp
        output = ((x_value-x_center)**2+(y_center-y_value)**2)**0.5

        return output
    def find_angle(self, point_tuple, adjustment, time_unit):
        x_differential = point_tuple[0] - self.cut_center[0]
        y_differential = self.cut_center[1] - point_tuple[1]  # REMEMBER Y IS BACKWARDS FOR TRIG
        if x_differential == 0:
            if y_differential > 0:
                angle = 0
            else:
                angle = 180
        else:

            if x_differential > 0:  # Quadrent I
                angle = 360-(math.atan(y_differential/x_differential)+3*math.pi/2)*180/math.pi+adjustment
            else:
                angle = (2*math.pi - math.atan(y_differential/x_differential)+3*math.pi/2)*180/math.pi+adjustment-360
        if time_unit == "hour":
            angle_per_hour = 30
            hour_count_raw = angle/angle_per_hour

            return hour_count_raw
        elif time_unit == "minute":
            angle_per_minute = 6
            minute_count_raw = angle/angle_per_minute
            return minute_count_raw
        elif time_unit == "second":
            angle_per_second = 6
            second_count_raw = angle/angle_per_second
            return second_count_raw
        else:
            pass
    def determining_the_time(self, hour_raw, minute_raw,second_raw):
        second = int(round(second_raw, 0))
        if second <= 30:
            minute = int(round(minute_raw,0))  # doing this because it should round to its nearest point here
        else:
            minute = int(math.floor(minute_raw))  # doing this because rounding does not apply at this point
        if minute <= 30:
            hour = int(round(hour_raw, 0))
        else:
            hour = int(math.floor(hour_raw))
        if hour == 0:
            hour = 12
        if minute == 60:
            minute = 0
        if second == 60:
            second = 0
        hour = str(hour)
        minute = str(minute)
        second = str(second)
        a = (hour, minute, second)
        b = []
        for item in a:
            if len(item) == 1:
                item = "0{}".format(item)
            b.append(item)
        return (b)

    def process(self):
        clock_im_base = self.image
        clock_im = clock_im_base[(self.center[1] - self.bsp):(self.center[1] + self.bsp), (self.center[0] - self.bsp):(self.center[0] + self.bsp)]
        yellow_range = cv2.inRange(clock_im, (30, 220, 190), (210, 245, 255))
        cv2.dilate(yellow_range, (1,1), iterations=2)
        red_range = cv2.inRange(clock_im, (75,85,145), (130,150,255))
        cv2.dilate(red_range, (1,1), iterations=2)
        y_cnts = cv2.findContours(yellow_range.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)

        b_cnts = cv2.findContours(red_range.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)
        if y_cnts[1] is not None and b_cnts[1] is not None:
            y_cnts = imutils.grab_contours(y_cnts)
            y_cnts = sorted(y_cnts,key=cv2.contourArea, reverse=True)
            y_c = y_cnts[0]
            g_c = y_cnts[1]


            b_cnts = imutils.grab_contours(b_cnts)
            b_cnts = sorted(b_cnts,key=cv2.contourArea, reverse=True)
            b_c = max(b_cnts, key=cv2.contourArea)
            y_approx = sorted(y_c, key=self.distance_from_center, reverse=True)
            g_approx = sorted(g_c, key=self.distance_from_center, reverse=True)
            b_approx = sorted(b_c, key=self.distance_from_center, reverse=True)
            y_point = y_approx[0]
            g_point = g_approx[0]
            b_point = b_approx[0]
            hour_raw = (self.find_angle(b_point[0], 0,'hour'))
            minute_raw = (self.find_angle(y_point[0], 0, 'minute'))
            second_raw = (self.find_angle(g_point[0], 0, 'second'))  # 180 degrees
            time_result = self.determining_the_time(hour_raw,minute_raw,second_raw)
            text = "The Time recorded is {0}:{1}:{2}".format(time_result[0],time_result[1],time_result[2])
            font = cv2.FONT_HERSHEY_SIMPLEX
            org = (650, 60)

            # fontScale
            fontScale = 2

            # Red color in BGR
            color = (0, 0, 255)

            # Line thickness of 2 px
            thickness = 5

            # Using cv2.putText() method
            image = cv2.putText(clock_im_base, text, org, font, fontScale,
                                color, thickness, cv2.LINE_AA, False)


            cv2.circle(img=clock_im, center=(y_point[0][0], y_point[0][1]),radius=5, color=(0,0,255),thickness=-5)
            cv2.circle(img=clock_im, center=(g_point[0][0], g_point[0][1]),radius=5, color=(0,255,0),thickness=-5)
            cv2.circle(img=clock_im, center=(b_point[0][0], b_point[0][1]),radius=5, color=(255,0,0),thickness=-5)
        cv2.circle(img=clock_im_base, center=(self.center),radius=10, color=(255,0,0),thickness=3)
        cv2.rectangle(img=clock_im_base,
                      pt1=(self.center[0] - self.bsp, self.center[1] - self.bsp),
                      pt2=(self.center[0] + self.bsp, self.center[1] + self.bsp),
                      color=(255,0,255), thickness=3)
        # REMOVE PLEASE

        cv2.imshow("result", clock_im)
        cv2.imshow("base", clock_im_base)
        cv2.imshow("red", red_range)
        cv2.imshow("yellow", yellow_range)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('clock_color_read.png', clock_im_base)


cap = cv2.VideoCapture(0)
l = 0
while cap.isOpened():
    if l > 5:
        crap = cap.read()[0]
        nice_try = clock_reader()
        clock_reader.process(nice_try)

    else:
        l += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()