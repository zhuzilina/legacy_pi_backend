from django.urls import path
from . import views

app_name = 'md_docs'

urlpatterns = [
    # 核心API：根据类别获取文档列表
    path('category/', views.get_documents_by_category, name='documents_by_category'),
    
    # 核心API：根据文档ID获取Markdown内容
    path('document/<str:document_id>/', views.get_document_markdown, name='document_markdown'),
    
    # 辅助API：获取文档系统状态
    path('status/', views.get_document_status, name='document_status'),
    
    # 图片API：获取文档图片
    path('image/<str:image_id>/', views.get_document_image, name='document_image'),
    
    # 管理API：上传文档
    path('upload/', views.upload_document, name='upload_document'),
    
    # 管理API：上传图片
    path('upload-image/', views.upload_image, name='upload_image'),
]
