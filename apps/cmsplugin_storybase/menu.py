from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from menus.base import Menu, Modifier, NavigationNode 
from menus.menu_pool import menu_pool

from cmsplugin_storybase import settings as plugin_settings

from storybase_user.models import Organization, Project

class StorybaseMenu(Menu):
    """
    Add views from the various StoryBase apps to the CMS menu
    """
    def get_nodes(self, request): 
        nodes = []
        build = NavigationNode(
            title=_(plugin_settings.STORYBASE_BUILD_TITLE),
            url=reverse('story_builder'), id='build')
        nodes.append(build)
        explore = NavigationNode(
            title=_(plugin_settings.STORYBASE_EXPLORE_TITLE),
            url=reverse('explore_stories'), id='explore')
        nodes.append(explore)
        organizations = NavigationNode(
            title=_(plugin_settings.STORYBASE_ORGANIZATION_LIST_TITLE),
            url=reverse('organization_list'),
            id='organizations',
            parent_id=explore.id)
        nodes.append(organizations)
        for organization in Organization.objects.all().order_by('organizationtranslation__name'):
            nodes.append(
            NavigationNode(
                title=organization.name,
                url=organization.get_absolute_url(),
                id=organization.organization_id,
                parent_id=organizations.id))
        projects = NavigationNode(
            title=_(plugin_settings.STORYBASE_PROJECT_LIST_TITLE), 
            url=reverse('project_list'),
            id='projects',
            parent_id=explore.id)
        nodes.append(projects)
        for project in Project.objects.all().order_by('-last_edited'):
            nodes.append(
                NavigationNode(
	                title=project.name,
                    url=project.get_absolute_url(),
                    id=project.project_id,
                    parent_id=projects.id))
                                        
        return nodes

menu_pool.register_menu(StorybaseMenu)

class OrderMenuNodes(Modifier):
    """Modifier that insert custom navigation nodes in a specified order"""
    def move_node(self, nodes, id, position):
        modified_nodes = []
        matched_node = None
        matched_children = []
        # Check to make sure we're trying to insert the explore menu nodes
	    # in a position that actually exists
        insert_at = position if position < len(nodes) else len(nodes) - 1
        print insert_at
        for node in nodes:
           # Discover nodes in the explore menu and separate them
           if node.id == id:
               matched_node = node
               matched_children.append(node)
           elif matched_node in node.get_ancestors():
	           matched_children.append(node)
           else:
               modified_nodes.append(node)

        # Add the explore nodes back at the specified position
        for node in matched_children:
            modified_nodes.insert(insert_at, node)
            insert_at += 1

        return modified_nodes

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut:
            return nodes

        modified_nodes = self.move_node(nodes, 'explore', 
            plugin_settings.STORYBASE_EXPLORE_MENU_POSITION)
        modified_nodes = self.move_node(modified_nodes, 'build',
            plugin_settings.STORYBASE_BUILD_MENU_POSITION)

        return modified_nodes

menu_pool.register_modifier(OrderMenuNodes)
