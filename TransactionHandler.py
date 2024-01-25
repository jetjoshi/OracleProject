import sqlite3
import queue
import threading

class TransactionHandler:
    def __init__(self, db_path='locations.db'):
        self.db_path = db_path
        self.transaction_queue = queue.Queue()
        self.result_dict = {}
        self.worker_thread = threading.Thread(target=self._process_transactions, daemon=True)
        self.worker_thread.start()

    def _process_transactions(self):
        while True:
            # Get the transactions from the queue
            transaction = self.transaction_queue.get()

            # Check for the termination signal
            if transaction.get('is_termination', False):
                break

            try:
                # Connect to the SQLite database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                query = transaction['query']
                params = transaction.get('params', ())
                is_select = transaction.get('is_select', False)

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch and store the result for SELECT queries
                if is_select:
                    result = cursor.fetchall()
                    self.result_dict[transaction['id']] = result

                # Commit the changes and close the connection
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error executing transactions: {str(e)}")

            # Mark the transaction as done and remove it from the queue
            self.transaction_queue.task_done()

    def add_transaction(self, query, params=None, is_select=False, is_termination=False):
        # Generate a unique ID for the transaction
        transaction_id = hash((query, is_select))
        # Put the transaction into the queue
        self.transaction_queue.put({'id': transaction_id, 'query': query, 'params': params, 'is_select': is_select})

        # Wait for the result of the transaction and return it immediately
        while transaction_id not in self.result_dict and is_select:
            pass  # Wait for the result to be available
        result = self.result_dict.pop(transaction_id) if is_select else None
        return result

    def wait_for_completion(self):
        # Block until all transactions in the queue are processed
        self.transaction_queue.join()

    def stop(self):
        # Add a termination signal to stop the worker thread
        self.transaction_queue.put({'is_termination': True})
        # Wait for the worker thread to finish
        self.worker_thread.join()


