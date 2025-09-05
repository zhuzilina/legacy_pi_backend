from django import forms
from django.utils.safestring import mark_safe


class OptionsWidget(forms.Textarea):
    """简化的JSON选项编辑Widget"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 8, 
            'cols': 80,
            'style': 'font-family: monospace; font-size: 12px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        import json
        
        # 如果没有值，提供默认模板
        if not value:
            default_template = [
                {"text": "选项A", "is_correct": True},
                {"text": "选项B", "is_correct": False},
                {"text": "选项C", "is_correct": False}
            ]
            value = json.dumps(default_template, ensure_ascii=False, indent=2)
        
        # 如果有值但不是格式化的JSON，尝试格式化
        elif isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
                value = json.dumps(parsed, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, TypeError, ValueError):
                # 如果解析失败，保持原值
                pass
        
        # 生成HTML
        final_attrs = self.build_attrs(attrs or {})
        attrs_str = ' '.join([f'{k}="{v}"' for k, v in final_attrs.items()])
        
        html = f'''
        <div style="margin-bottom: 15px;">
            <div style="margin-bottom: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; font-size: 12px; color: #666;">
                <strong>选项格式说明：</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>请使用JSON格式编辑选项</li>
                    <li>每个选项包含"text"（选项内容）和"is_correct"（是否为正确答案）</li>
                    <li>单选题只能有一个"is_correct": true</li>
                    <li>多选题可以有多个"is_correct": true</li>
                </ul>
            </div>
            <textarea name="{name}" id="id_{name}" {attrs_str}>{value}</textarea>
        </div>
        '''
        
        return mark_safe(html)
    
    def value_from_datadict(self, data, files, name):
        """从表单数据中获取值"""
        return data.get(name, '')
    
    def format_value(self, value):
        """格式化值用于显示"""
        import json
        
        if not value:
            return ''
        
        if isinstance(value, str):
            try:
                # 尝试解析并重新格式化JSON
                parsed = json.loads(value)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            except (json.JSONDecodeError, TypeError, ValueError):
                return value
        
        return value


class ChoiceQuestionForm(forms.ModelForm):
    """选择题表单"""
    
    class Meta:
        from .models import ChoiceQuestion
        model = ChoiceQuestion
        fields = '__all__'
        widgets = {
            'options': OptionsWidget(),
            'question_text': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
            'explanation': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }
    
    def clean_options(self):
        """验证选项数据"""
        import json
        
        options_data = self.cleaned_data.get('options', '')
        
        # 如果已经是列表，直接使用
        if isinstance(options_data, list):
            options = options_data
        else:
            # 如果是字符串，检查是否为空
            if not options_data or (isinstance(options_data, str) and not options_data.strip()):
                raise forms.ValidationError('选项不能为空')
            
            # 解析JSON数据
            try:
                options = json.loads(options_data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                raise forms.ValidationError(f'选项数据格式错误: {str(e)}')
        
        # 确保options是一个列表
        if not isinstance(options, list):
            raise forms.ValidationError('选项数据必须是数组格式')
        
        # 检查是否有选项
        if not options:
            raise forms.ValidationError('至少需要添加一个选项')
        
        # 验证每个选项的格式
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                raise forms.ValidationError(f'第{i+1}个选项格式错误')
            
            if 'text' not in option or not option['text'].strip():
                raise forms.ValidationError(f'第{i+1}个选项内容不能为空')
            
            if 'is_correct' not in option:
                raise forms.ValidationError(f'第{i+1}个选项缺少正确答案标记')
        
        # 检查是否有正确答案
        correct_options = [opt for opt in options if opt.get('is_correct', False)]
        if not correct_options:
            raise forms.ValidationError('至少需要设置一个正确答案')
        
        # 对于单选题，只能有一个正确答案
        if self.cleaned_data.get('question_type') == 'single' and len(correct_options) > 1:
            raise forms.ValidationError('单选题只能有一个正确答案')
        
        # 返回JSON字符串供模型保存
        return json.dumps(options, ensure_ascii=False)