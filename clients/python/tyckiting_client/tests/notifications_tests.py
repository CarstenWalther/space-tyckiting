import unittest

import tyckiting_client.notifications as notifications

class NotificationsTests(unittest.TestCase):

    def test_register_class_function(self):
        notif_id = 'bla'

        class Test:
            def incVal(self, notification):
                self.val += 1
                self.notif_data = notification.data

            def __init__(self):
                self.val = 0
                notifications.defaultNotificationCenter.registerFunc(notif_id, self.incVal)

        test = Test()
        self.assertEqual(test.val, 0)

        notification = notifications.Notification(notif_id, {})
        notifications.defaultNotificationCenter.send(notification)
        self.assertEqual(test.val, 1)
        self.assertEqual(test.notif_data, {})
