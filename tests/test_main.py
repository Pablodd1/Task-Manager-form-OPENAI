import unittest
import json
from app.main import app, tasks

class TaskManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Reset tasks for each test
        tasks.clear()
        # Add initial task with new fields
        tasks.append({
            'id': 1,
            'title': 'Task 1',
            'description': 'Desc 1',
            'assignee': 'John',
            'assignee_email': 'john@example.com',
            'due_date': '2023-12-31',
            'status': 'Todo'
        })

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task Manager', response.data)

    def test_get_tasks(self):
        response = self.app.get('/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], 'Task 1')
        self.assertEqual(data['tasks'][0]['status'], 'Todo')

    def test_get_task(self):
        response = self.app.get('/tasks/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'Task 1')

    def test_get_task_not_found(self):
        response = self.app.get('/tasks/999')
        self.assertEqual(response.status_code, 404)

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
        self.assertEqual(data['task']['assignee'], 'Jane')
        self.assertEqual(data['task']['status'], 'Todo')
        self.assertEqual(len(tasks), 2)

    def test_update_task_status(self):
        update_data = {'status': 'Done'}
        response = self.app.put('/tasks/1', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['task']['status'], 'Done')
        self.assertEqual(tasks[0]['status'], 'Done')

    def test_delete_task(self):
        response = self.app.delete('/tasks/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(tasks), 0)

    def test_add_task_bad_request(self):
        response = self.app.post('/tasks', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_reminders(self):
        # Task 1 is 'Todo' and has email, should send reminder
        response = self.app.post('/api/cron/reminders')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['sent'], 1)
        self.assertIn('Sending reminder to john@example.com', data['logs'][0])

        # Mark as done
        self.app.put('/tasks/1', data=json.dumps({'status': 'Done'}), content_type='application/json')

        # Should not send reminder now
        response = self.app.post('/api/cron/reminders')
        data = json.loads(response.data)
        self.assertEqual(data['sent'], 0)

if __name__ == '__main__':
    unittest.main()
