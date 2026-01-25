import unittest
import json
import app.main as main_module
from app.main import app, TASKS, Task

class TaskManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Reset Global State
        main_module.TASKS.clear()
        main_module.NEXT_ID = 1

        # Add initial task
        task = Task(
            id=main_module.NEXT_ID,
            title='Task 1',
            description='Desc 1',
            assignee='John',
            assignee_email='john@example.com',
            due_date='2023-12-31',
            status='Todo'
        )
        main_module.TASKS[main_module.NEXT_ID] = task
        main_module.NEXT_ID += 1

    def tearDown(self):
        main_module.TASKS.clear()
        main_module.NEXT_ID = 1

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Team Task Manager', response.data)

    def test_get_tasks(self):
        response = self.app.get('/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], 'Task 1')

    def test_add_task(self):
        new_task = {
            'title': 'New Task',
            'description': 'New Desc',
            'assignee': 'Jane',
            'assignee_email': 'jane@example.com',
            'due_date': '2024-01-01'
        }
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'New Task')

        # Verify In-Memory Store
        self.assertEqual(len(main_module.TASKS), 2)

    def test_update_task(self):
        update_data = {'status': 'Done'}
        response = self.app.put('/tasks/1', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        task = main_module.TASKS.get(1)
        self.assertEqual(task.status, 'Done')

    def test_delete_task(self):
        response = self.app.delete('/tasks/1')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(main_module.TASKS), 0)

    def test_reminders_simulation(self):
        # Should attempt to send email (but fail/skip because no credentials in test env)
        response = self.app.post('/api/cron/reminders')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['processed'], 1)
        self.assertIn("Skipped (No Config)", data['logs'][0])

if __name__ == '__main__':
    unittest.main()
