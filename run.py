import websocket
import json
import requests
import threading
import ssl

class IGMarketsWebSocket:
    def __init__(self, api_key, account_id, api_password):
        self.base_url = "https://demo-api.ig.com/gateway/deal"
        self.api_key = api_key
        self.account_id = account_id
        self.api_password = api_password
        self.session_token = None
        self.cst = None
        self.lightstreamer_endpoint = None
        self.ws = None

    def login(self):
        headers = {
            'X-IG-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=UTF-8'
        }
        
        data = {
            'identifier': self.account_id,
            'password': self.api_password
        }
        
        response = requests.post(f"{self.base_url}/session", headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            self.session_token = response.headers['X-SECURITY-TOKEN']
            self.cst = response.headers['CST']
            self.lightstreamer_endpoint = response.json()['lightstreamerEndpoint']
            return True
        return False

    def create_subscription(self, epic):
        session_url = f"{self.lightstreamer_endpoint}/lightstreamer/create_session.txt"
        session_params = {
            "LS_op2": 'create',
            "LS_cid": 'mgQkwtwdysogQz2BJ4Ji kOj2Bg',
            "LS_user": self.account_id,
            "LS_password": f"CST-{self.cst}|XST-{self.session_token}"
        }
        response = requests.post(session_url, data=session_params)
        session_id = response.text.split(":")[-1].strip()

        control_url = f"{self.lightstreamer_endpoint}/lightstreamer/control.txt"
        control_params = {
            "LS_session": session_id,
            "LS_op": 'add',
            "LS_table": '1',
            "LS_id": f"MARKET:{epic}",
            "LS_schema": "UPDATE_TIME BID OFFER CHANGE MARKET_STATE",
            "LS_mode": 'MERGE'
        }
        requests.post(control_url, data=control_params)

        return session_id

    def on_message(self, ws, message):
        print(f"Received: {message}")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        print("Opened connection")

    def connect_websocket(self, session_id):
        websocket_url = f"{self.lightstreamer_endpoint}/lightstreamer/bind_session.txt?LS_session={session_id}"
        self.ws = websocket.WebSocketApp(websocket_url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        
        wst = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
        wst.daemon = True
        wst.start()

def main():
    api_key = "YOUR_API_KEY"
    account_id = "YOUR_ACCOUNT_ID"
    api_password = "YOUR_API_PASSWORD"
    
    ig = IGMarketsWebSocket(api_key, account_id, api_password)
    
    if ig.login():
        print("Logged in successfully")
        
        epic = "CS.D.EURUSD.TODAY.IP"  # Example: EUR/USD
        session_id = ig.create_subscription(epic)
        ig.connect_websocket(session_id)
        
        # Keep the main thread running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ig.ws.close()
            print("WebSocket connection closed")
    else:
        print("Login failed")

if __name__ == "__main__":
    main()