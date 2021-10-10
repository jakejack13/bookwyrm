""" testing models """
from unittest.mock import patch
from django.test import TestCase

from bookwyrm import models, settings


@patch("bookwyrm.models.activitypub_mixin.broadcast_task.delay")
class Group(TestCase):
    """some activitypub oddness ahead"""

    def setUp(self):
        """Set up for tests"""

        self.owner_user = models.User.objects.create_user(
            "mouse", "mouse@mouse.mouse", "mouseword", local=True, localname="mouse"
        )

        self.rat = models.User.objects.create_user(
            "rat", "rat@rat.rat", "ratword", local=True, localname="rat"
        )

        self.badger = models.User.objects.create_user(
            "badger", "badger@badger.badger", "badgerword", local=True, localname="badger"
        )

        self.capybara = models.User.objects.create_user(
            "capybara", "capybara@capybara.capybara", "capybaraword", local=True, localname="capybara"
        )

        self.public_group = models.Group.objects.create(
            name="Public Group", 
            description="Initial description",
            user=self.owner_user, 
            privacy="public"
        )

        self.private_group = models.Group.objects.create(
            name="Private Group", 
            description="Top secret",
            user=self.owner_user, 
            privacy="direct"
        )

        self.followers_only_group = models.Group.objects.create(
            name="Followers Group", 
            description="No strangers",
            user=self.owner_user, 
            privacy="followers"
        )

        self.followers_list = models.List.objects.create(
            name="Followers List",
            curation="group",
            privacy="followers",
            group=self.public_group,
            user=self.owner_user
        )

        self.private_list = models.List.objects.create(
            name="Private List",
            privacy="direct",
            curation="group",
            group=self.public_group,
            user=self.owner_user
        )

        models.GroupMember.objects.create(
            group=self.private_group, user=self.badger
        )
        models.GroupMember.objects.create(
            group=self.followers_only_group, user=self.badger
        )
        models.GroupMember.objects.create(
            group=self.public_group, user=self.capybara
        )

    def test_group_members_can_see_followers_only_groups(self, _):
        """follower-only group should not be excluded from group listings for group members viewing"""

        rat_groups = models.Group.privacy_filter(self.rat).all()
        badger_groups = models.Group.privacy_filter(self.badger).all()

        self.assertFalse(self.followers_only_group in rat_groups)
        self.assertTrue(self.followers_only_group in badger_groups)

    def test_group_members_can_see_private_groups(self, _):
        """direct privacy group should not be excluded from group listings for group members viewing"""

        rat_groups = models.Group.privacy_filter(self.rat).all()
        badger_groups = models.Group.privacy_filter(self.badger).all()

        self.assertFalse(self.private_group in rat_groups)
        self.assertTrue(self.private_group in badger_groups)

    def test_group_members_can_see_followers_only_lists(self, _):
        """follower-only group booklists should not be excluded from group booklist listing for group members who do not follower list owner"""

        rat_lists = models.List.privacy_filter(self.rat).all()
        badger_lists = models.List.privacy_filter(self.badger).all()
        capybara_lists = models.List.privacy_filter(self.capybara).all()

        self.assertFalse(self.followers_list in rat_lists)
        self.assertFalse(self.followers_list in badger_lists)
        self.assertTrue(self.followers_list in capybara_lists)
        
    def test_group_members_can_see_private_lists(self, _):
        """private group booklists should not be excluded from group booklist listing for group members"""

        rat_lists = models.List.privacy_filter(self.rat).all()
        badger_lists = models.List.privacy_filter(self.badger).all()
        capybara_lists = models.List.privacy_filter(self.capybara).all()

        self.assertFalse(self.private_list in rat_lists)
        self.assertFalse(self.private_list in badger_lists)
        self.assertTrue(self.private_list in capybara_lists)
