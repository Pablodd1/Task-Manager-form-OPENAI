import unittest
import json
from app.main import app, tasks

class TaskManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Reset tasks for each test
        tasks.clear()
        tasks.append({'id': 1, 'title': 'Task 1', 'description': 'Desc 1', 'done': False})

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

    def test_get_task(self):
        response = self.app.get('/tasks/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'Task 1')

    def test_get_task_not_found(self):
        response = self.app.get('/tasks/999')
        self.assertEqual(response.status_code, 404)

    def test_add_task(self):
        new_task = {'title': 'New Task', 'description': 'New Desc'}
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'New Task')
        self.assertEqual(len(tasks), 2)

    def test_update_task(self):
        update_data = {'done': True}
        response = self.app.put('/tasks/1', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['task']['done'])
        self.assertTrue(tasks[0]['done'])

    def test_delete_task(self):
        response = self.app.delete('/tasks/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(tasks), 0)

    def test_add_task_bad_request(self):
        response = self.app.post('/tasks', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_task_not_found(self):
        response = self.app.put('/tasks/999', data=json.dumps({'done': True}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_task_not_found(self):
        response = self.app.delete('/tasks/999')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
