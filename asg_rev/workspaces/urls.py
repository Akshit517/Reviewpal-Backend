from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from workspaces.views.workspace import (
    WorkspaceViewSet,
    WorkspaceMemberView,
    AcceptWorkspaceInviteView
)
from workspaces.views.category import (
    CategoryViewSet,
    CategoryMemberView,
)
from workspaces.views.channel import (
    ChannelViewSet,
    ChannelMemberView,
)
from workspaces.views.assignment import (
    AssignmentView
)
from workspaces.views.submission import (
    SubmissionRevieweeView,
    SubmissionReviewerView,
)
from workspaces.views.submission_detail import (
    SubmissionDetailView
)
from workspaces.views.iteration import (
    RevieweeIterationView,
    ReviewerIterationView
)

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspaces')

workspaces_router = routers.NestedDefaultRouter(router, r'workspaces', lookup='workspace')
workspaces_router.register(r'categories', CategoryViewSet, basename='workspace-categories')

categories_router = routers.NestedDefaultRouter(workspaces_router, r'categories', lookup='category')
categories_router.register(r'channels', ChannelViewSet, basename='category-channels')

prefix_url = 'api/'

urlpatterns = [
    path(f'{prefix_url}', include(router.urls)),
    path(f'{prefix_url}', include(workspaces_router.urls)),
    path(f'{prefix_url}', include(categories_router.urls)),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/members/', 
        WorkspaceMemberView.as_view(), 
        name='workspace-member'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/members/', 
        CategoryMemberView.as_view(), 
        name='category-member'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/members/', 
        ChannelMemberView.as_view(), 
        name='channel-member'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:pk>/assignment/',
        AssignmentView.as_view(), 
        name="assignment"
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/submissions/reviewee/', 
        SubmissionRevieweeView.as_view(), 
        name='submission-reviewee'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/submissions/reviewer/', 
        SubmissionReviewerView.as_view(), 
        name='submission-reviewer'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/submissions/<int:user_id>/', 
        SubmissionReviewerView.as_view(), 
        name='submission-reviewer-user'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/submissions/<int:submission_id>/reviewer-iterations/',
        ReviewerIterationView.as_view(),
        name='reviewer-iterations'
    ),
    path(
        f'{prefix_url}workspaces/<uuid:workspace_pk>/categories/<int:category_pk>/channels/<uuid:channel_pk>/submissions/<int:submission_id>/reviewee-iterations/',
        RevieweeIterationView.as_view(),
        name='reviewee-iterations'
    ),
    path('api/workspaces/<uuid:workspace_pk>/accept-invite/<str:token>/<str:uidb64>/<str:role>/',
         AcceptWorkspaceInviteView.as_view(),
         name='accept_workspace_invite'),
]