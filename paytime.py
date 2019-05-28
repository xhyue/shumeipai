import datetime
__author__ = 'TonyQu'
## This example create by Tony Qu in 2019-03-int(per_se_money)
## It includes some basic function about the money of car
## PLEASE NOTE: This example maybe have some bug
## If you have trouble installing it, try any of the other demos
## that don't require it instead.
# in_time: 汽车驶入时间
# out_time: 汽车驶出时间
# f_time：白天开始计费节点
# s_time：白天结束计费节点
# early_money：清晨价格
# day_money：白天价格
# night_money：夜间价格
# all_day_money：全天价格
# fixed_hour_money:固定每小时价格


class ShareToPay(object):

    def __init__(self, in_time, out_time, f_time, s_time, early_money, day_money, night_money, all_day_money, per_se_money):
        self.__in_time = in_time
        self.__out_time = out_time
        self.__f_time = f_time
        self.__s_time = s_time
        self.__early_money = early_money
        self.__day_money = day_money
        self.__night_money = night_money
        self.__all_day_money = all_day_money
        self.__per_se_money = per_se_money
        self.__money = self.shtopay()

    def get_money(self):
        return self.__money

    def shtopay(self):
        early_money = self.__early_money
        day_money = self.__day_money
        night_money = self.__night_money
        all_day_money = self.__all_day_money
        per_se_money = self.__per_se_money
        money = {}
        f_time = self.__f_time
        s_time = self.__s_time
        f_time_d = datetime.datetime.strptime(f_time, '%H%M%S')
        s_time_d = datetime.datetime.strptime(s_time, '%H%M%S')
        in_time = str(self.__in_time)
        out_time = str(self.__out_time)
        in_time_d = datetime.datetime.strptime(in_time, '%Y%m%d%H%M%S')
        out_time_d = datetime.datetime.strptime(out_time, '%Y%m%d%H%M%S')
        in_time_date = in_time[:8]
        out_time_date = out_time[:8]
        all_days = (out_time_d-in_time_d).days
        in_time_time = in_time[-6:]
        out_time_time = out_time[-6:]
        in_time = datetime.datetime.strptime(in_time_time, '%H%M%S')
        out_time = datetime.datetime.strptime(out_time_time, '%H%M%S')
        if in_time_date != out_time_date:
            if int(in_time_time)>int(out_time_time):
                days_money = all_days * all_day_money
            else:
                all_days = all_days-1
                days_money = all_days * all_day_money
            if int(in_time_time) < int(f_time):
                i_e_money = early_money * int((f_time_d - in_time).seconds / 60 / int(per_se_money))
                i_d_money = day_money * int((s_time_d - f_time_d).seconds / 60 / int(per_se_money))
                i_n_money = night_money * int((datetime.datetime.strptime("000000", '%H%M%S') - s_time_d).seconds / 60 / int(per_se_money) )
                before_money = i_e_money + i_d_money + i_n_money
            elif int(in_time_time) >= int(f_time) and int(in_time_time) < int(s_time):
                i_e_money = 0
                i_d_money = day_money * int((s_time_d - in_time).seconds / 60 / int(per_se_money))
                i_n_money = night_money * int((datetime.datetime.strptime("000000", '%H%M%S') - s_time_d).seconds / 60 / int(per_se_money))
                before_money = i_e_money + i_d_money + i_n_money
            else:
                i_e_money = 0
                i_d_money = 0
                i_n_money = night_money * int((datetime.datetime.strptime("000000", '%H%M%S') - in_time).seconds / 60 / int(per_se_money))
                before_money = i_e_money + i_d_money + i_n_money
            if int(out_time_time) < int(s_time):
                o_e_money = early_money * int((out_time - datetime.datetime.strptime("000000", '%H%M%S')).seconds / 60 / int(per_se_money))
                o_d_money = 0
                o_n_money = 0
                after_money = o_e_money + o_d_money + o_n_money
            elif int(out_time_time) >= int(f_time) and int(out_time_time) < int(s_time):
                o_e_money = early_money * int((f_time_d - datetime.datetime.strptime("000000", '%H%M%S')).seconds / 60 / int(per_se_money))
                o_d_money = day_money * int((out_time - f_time_d).seconds / 60 / int(per_se_money))
                o_n_money = 0
                after_money = o_e_money + o_d_money + o_n_money
            else:
                o_e_money = early_money * int((f_time_d - datetime.datetime.strptime("000000", '%H%M%S')).seconds / 60 / int(per_se_money))
                o_d_money = day_money * int((s_time_d - f_time_d).seconds / 60 / int(per_se_money))
                o_n_money = night_money * int((out_time - s_time_d).seconds / 60 / int(per_se_money))
                after_money = o_e_money + o_d_money + o_n_money
            total_money = days_money + before_money + after_money
            money['i_e_money'] = i_e_money
            money['i_d_money'] = i_d_money
            money['i_n_money'] = i_n_money
            money['o_e_money'] = o_e_money
            money['o_d_money'] = o_d_money
            money['o_n_money'] = o_n_money
            money['total_money'] = total_money
        else:
            if int(in_time_time)<int(f_time) and int(out_time_time)<int(f_time):
                i_e_money = early_money * int((out_time - in_time).seconds / 60 / int(per_se_money))
                i_d_money = 0
                i_n_money = 0
                before_money = i_e_money + i_d_money + i_n_money
            elif int(in_time_time)<int(f_time) and int(out_time_time) >=int(f_time) and int(out_time_time)<int(s_time):
                i_e_money = early_money * int((f_time_d - in_time).seconds / 60 / int(per_se_money))
                i_d_money = day_money * int((out_time - f_time_d).seconds / 60 / int(per_se_money))
                i_n_money = 0
                before_money = i_e_money + i_d_money + i_n_money
            elif int(in_time_time)<=int(f_time) and int(out_time_time) >=int(s_time):
                i_e_money = early_money * int((f_time_d - in_time).seconds / 60 / int(per_se_money))
                i_d_money = day_money * int((s_time_d - f_time_d).seconds / 60 / int(per_se_money))
                i_n_money = night_money * int((out_time - s_time_d).seconds / 60 / int(per_se_money))
                before_money = i_e_money + i_d_money + i_n_money
            if int(in_time_time) >= int(f_time) and int(out_time_time) < int(s_time):
                i_e_money = 0
                i_d_money = day_money * int((out_time - in_time).seconds / 60 / int(per_se_money))
                i_n_money = 0
                before_money = i_e_money + i_d_money + i_n_money
            elif int(in_time_time) >= int(f_time) and int(out_time_time) >= int(s_time):
                i_e_money = 0
                i_d_money = day_money * int((s_time_d - in_time).seconds / 60 / int(per_se_money))
                i_n_money = night_money * int((out_time - s_time_d).seconds / 60 / int(per_se_money))
                before_money = i_e_money + i_d_money + i_n_money
            if int(in_time_time) >= int(s_time):
                i_e_money = 0
                i_d_money = 0
                i_n_money = night_money * int((out_time - in_time).seconds / 60 / int(per_se_money))
            days_money = 0
            after_money = 0
            total_money = days_money + before_money + after_money
            money['i_e_money'] = i_e_money
            money['i_d_money'] = i_d_money
            money['i_n_money'] = i_n_money
            money['total_money'] = total_money
        return money


class FixedToPay(object):
    def __init__(self, in_time, out_time, fixed_hour_money):
        self.__in_time = in_time
        self.__out_time = out_time
        self.__fixed_hour_money = fixed_hour_money
        self.__money = self.shtopay()

    def get_money(self):
        return self.__money

    def shtopay(self):
        in_time = str(self.__in_time)
        out_time = str(self.__out_time)
        fixed_hour_money = self.__fixed_hour_money
        in_time = datetime.datetime.strptime(in_time, '%Y%m%d%H%M%S')
        out_time = datetime.datetime.strptime(out_time, '%Y%m%d%H%M%S')
        total_seconds = (out_time - in_time).total_seconds()
        total_hours = round(total_seconds / 60 / 60)
        total_money = total_hours * fixed_hour_money
        return total_money


# if __name__ == '__main__':
#     result = ShouldToPay("20190101050410", "20190105000400", "080000", "200000", 1, 2, 1, 4)
#     print(result.get_money())