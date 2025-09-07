# Generated manually for data migration

from django.db import migrations, models
import django.db.models.deletion


def migrate_questions_data(apps, schema_editor):
    """迁移现有题目数据到新的统一Question模型"""
    # 获取模型
    Question = apps.get_model('knowledge_quiz', 'Question')
    ChoiceQuestion = apps.get_model('knowledge_quiz', 'ChoiceQuestion')
    FillQuestion = apps.get_model('knowledge_quiz', 'FillQuestion')
    
    # 迁移选择题
    for choice_q in ChoiceQuestion.objects.all():
        question_type = 'choice_single' if choice_q.question_type == 'single' else 'choice_multiple'
        Question.objects.create(
            id=choice_q.id,
            question_text=choice_q.question_text,
            question_type=question_type,
            difficulty=choice_q.difficulty,
            category=choice_q.category,
            explanation=choice_q.explanation,
            tags=choice_q.tags,
            options=choice_q.options,
            correct_answer=None,
            created_at=choice_q.created_at,
            updated_at=choice_q.updated_at
        )
    
    # 迁移填空题
    for fill_q in FillQuestion.objects.all():
        Question.objects.create(
            id=fill_q.id,
            question_text=fill_q.question_text,
            question_type='fill',
            difficulty=fill_q.difficulty,
            category=fill_q.category,
            explanation=fill_q.explanation,
            tags=fill_q.tags,
            options=None,
            correct_answer=fill_q.correct_answer,
            created_at=fill_q.created_at,
            updated_at=fill_q.updated_at
        )


def reverse_migrate_questions_data(apps, schema_editor):
    """反向迁移：从统一Question模型恢复到原来的模型"""
    # 获取模型
    Question = apps.get_model('knowledge_quiz', 'Question')
    ChoiceQuestion = apps.get_model('knowledge_quiz', 'ChoiceQuestion')
    FillQuestion = apps.get_model('knowledge_quiz', 'FillQuestion')
    
    # 清空新表
    Question.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge_quiz', '0001_initial'),
    ]

    operations = [
        # 1. 创建新的Question模型
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(verbose_name='题目内容')),
                ('question_type', models.CharField(choices=[('choice_single', '单选题'), ('choice_multiple', '多选题'), ('fill', '填空题')], max_length=20, verbose_name='题目类型')),
                ('difficulty', models.CharField(choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难')], default='medium', max_length=10, verbose_name='难度')),
                ('category', models.CharField(choices=[('party_history', '党史'), ('theory', '理论')], default='party_history', max_length=20, verbose_name='分类')),
                ('explanation', models.TextField(blank=True, verbose_name='答案解析')),
                ('tags', models.CharField(blank=True, help_text='用逗号分隔多个标签', max_length=500, verbose_name='标签')),
                ('options', models.JSONField(blank=True, default=list, help_text='选择题的选项列表，格式：[{"text": "选项内容", "is_correct": true}]', null=True, verbose_name='选项')),
                ('correct_answer', models.TextField(blank=True, help_text='填空题的正确答案，多个答案用分号分隔', null=True, verbose_name='正确答案')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '题目',
                'verbose_name_plural': '题目',
                'ordering': ['-created_at'],
            },
        ),
        
        # 2. 迁移数据
        migrations.RunPython(migrate_questions_data, reverse_migrate_questions_data),
        
        # 3. 更新Answer模型
        migrations.RemoveField(
            model_name='answer',
            name='answer_type',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='choice_question',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='fill_question',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='knowledge_quiz.question', verbose_name='题目'),
            preserve_default=False,
        ),
        
        # 4. 更新DailyQuestion模型
        migrations.RemoveField(
            model_name='dailyquestion',
            name='question_id',
        ),
        migrations.RemoveField(
            model_name='dailyquestion',
            name='question_type',
        ),
        migrations.AddField(
            model_name='dailyquestion',
            name='question',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='knowledge_quiz.question', verbose_name='题目'),
            preserve_default=False,
        ),
    ]
