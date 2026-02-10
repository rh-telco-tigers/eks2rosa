# Message board (messages stored on PVC)

Simple web app: submit messages via the form; they are appended to a file on a PersistentVolumeClaim.

- **Stack:** Python 3.11 + Flask, no database.
- **Storage:** One PVC (`message-board-data`, 100Mi) mounted at `/data`; messages in `/data/messages.txt`.

## Deploy

```bash
kubectl apply -k examples/resources/message-board/
```

## Access

- **From inside the cluster:** `http://message-board/` (port 80).
- **From your machine:** port-forward then open http://localhost:8080

  ```bash
  kubectl port-forward svc/message-board 8080:80
  ```

## Send a message with curl

```bash
# With port-forward (localhost:8080)
curl -X POST -d "message=Hello from curl" http://localhost:8080/message

# From inside the cluster
kubectl exec deployment/message-board -- curl -s -X POST -d "message=Hello" http://localhost:8080/message
```

Then open the app in the browser (or `curl http://localhost:8080/`) to see the message. Data persists across pod restarts because it is on the PVC.
