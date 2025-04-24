import unittest
from core.event_queue import EventQueue
from core.event import Event

class TestEventQueue(unittest.TestCase):

    def test_event_ordering(self):
        eq = EventQueue()
        log = []

        def action1(): log.append("A")
        def action2(): log.append("B")
        def action3(): log.append("C")

        eq.schedule(Event(5, action2, "B"))
        eq.schedule(Event(1, action1, "A"))
        eq.schedule(Event(10, action3, "C"))

        eq.run()
        self.assertEqual(log, ["A", "B", "C"])

    def test_event_time_progression(self):
        eq = EventQueue()
        times = []

        def record_time():
            times.append(eq.current_time)

        eq.schedule(Event(2, record_time, "Record at 2"))
        eq.schedule(Event(5, record_time, "Record at 5"))

        eq.run()
        self.assertEqual(times, [2, 5])

    def test_no_events(self):
        eq = EventQueue()
        eq.run()
        self.assertEqual(eq.current_time, 0)

if __name__ == '__main__':
    unittest.main()
