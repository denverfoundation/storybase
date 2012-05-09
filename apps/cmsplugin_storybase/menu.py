from django.utils.translation import ugettext_lazy as _

from menus.base import Menu, Modifier, NavigationNode 
from menus.menu_pool import menu_pool

from cmsplugin_storybase import settings as plugin_settings

class StorybaseMenu(Menu):
    """
    Add views from the various StoryBase apps to the CMS menu
    """
    def get_nodes(self, request): 
	nodes = []
        explore = NavigationNode(title=_("Explore the Atlas"),
                                 url="/explore/", id='explore')
				 
	nodes.append(explore)
	projects = NavigationNode(title=_("Projects"), url="/projects/", 
			          id='projects',
				  parent_id=explore.id)
	nodes.append(projects)
	organizations = NavigationNode(title=_("Organizations"),
			               url="/organizations/",
				       id='organizations',
				       parent_id=explore.id)
	nodes.append(organizations)
        return nodes

menu_pool.register_menu(StorybaseMenu)

class OrderMenuNodes(Modifier):
    """Modifier that insert custom navigation nodes in a specified order"""
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut:
            return nodes

        modified_nodes = []
        explore_node = None
        explore_nodes = []
        insert_at = plugin_settings.STORYBASE_EXPLORE_MENU_POSITION
	# Dummy check in case the explore menu
	insert_at = insert_at if insert_at < len(nodes) else len(nodes) - 1
        for node in nodes:
           if node.id == 'explore':
                explore_node = node
                explore_nodes.append(node)	
           elif node in explore_node.children:
	        explore_nodes.append(node)	
           else:
                modified_nodes.append(node)
        for node in explore_nodes:
            modified_nodes.insert(insert_at, node) 
            insert_at += 1
        return modified_nodes

menu_pool.register_modifier(OrderMenuNodes)
