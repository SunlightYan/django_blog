# 引入表单类  forms.Form则需要手动配置每个字段，
# 它适用于不与数据库进行直接交互的功能。
# 用户登录不需要对数据库进行任何改动，因此直接继承forms.Form就可以了。
from django import forms
# 引入User模型
from django.contrib.auth.models import  User
# 引入Profile模型
from .models import Profile
# 登录表单，继承了 forms.Form 类
class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

class UserReisterForm(forms.ModelForm):
    # 复写User的密码 这里我们覆写了password字段，
    # 因为通常在注册时需要重复输入password来确保用户没有将密码输入错误，
    # 所以覆写掉它以便我们自己进行数据的验证工作。
    password = forms.CharField()
    # 验证密码一致性方法不能写def
    # clean_password()，因为如果你不定义def
    # clean_password2()
    # 方法，会导致password2中的数据被Django判定为无效数据从而清洗掉，从而password2属性不存在。最终导致两次密码输入始终会不一致，并且很难判断出错误原因。
    # 从POST中取值用的data.get('password')
    # 是一种稳妥的写法，即使用户没有输入密码也不会导致程序错误而跳出。前面章节提取POST数据我们用了data[
    # 'password']，这种取值方式如果data中不包含password，Django会报错。另一种防止用户不输入密码就提交的方式是在表单中插入required属性，后面会讲到。
    password2 = forms.CharField()

    class Meta:
        model = User
        # 覆写某字段之后，内部类class
        # Meta中的定义对这个字段就没有效果了，所以fields不用包含password。
        fields = ('username', 'email')

        # 对两次输入的密码是否一致进行检查
        # def clean_[字段]这种写法Django会自动调用，来对单个字段的数据进行验证清洗。
        def clean_password2(self):
            data = self.cleaned_data
            if data.get('password') == data.get('password2'):
                return data.get('password')
            else:
                raise forms.ValidationError("密码输入不一致，请重试。")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone','avatar','bio')
