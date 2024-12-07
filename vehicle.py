import cv2
import grpc
import vehicle_edge_pb2
import vehicle_edge_pb2_grpc
import time
import json

def capture_image():
    cap = cv2.VideoCapture("855848-hd_1920_1080_30fps.mp4")  # sample video
    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        cap.release()
        return buffer.tobytes()  
    cap.release()
    return None

def send_to_edge_server_image(image_data):
    # gRPC communication 
    channel = grpc.insecure_channel('localhost:50051')
    stub = vehicle_edge_pb2_grpc.EdgeServerStub(channel)
    response = stub.ProcessImage(vehicle_edge_pb2.ImageRequest(image=image_data))
    return response.result

def send_to_edge_server_route(start, goal):
    # gRPC 
    channel = grpc.insecure_channel('localhost:50051')
    stub = vehicle_edge_pb2_grpc.EdgeServerStub(channel)
    response = stub.PlanRoute(vehicle_edge_pb2.RouteRequest(start=start, goal=goal))
    return response.path

def process_predictions(predictions):
    print("Received Predictions:", predictions)

    if not predictions:
        print("No objects detected. Proceeding.")
        return "proceed"

    for obj in predictions:
        if obj['name'] == 'car' and obj['confidence'] > 0.8:
            print("Car detected with high confidence. Stopping!")
            return "stop"
        elif obj['name'] == 'person' and obj['confidence'] > 0.8:
            print("Person detected. Reducing speed!")
            return "slow down"

    print("No significant objects detected. Proceeding.")
    return "proceed"

if __name__ == "__main__":
    while True:
        # image capture and detection
        image_data = capture_image()
        if image_data:
            predictions_raw = send_to_edge_server_image(image_data)
            predictions = json.loads(predictions_raw)
            action = process_predictions(predictions)
            print(f"Action Taken: {action}")

        # route planning
        start = "A"
        goal = "D"
        route = send_to_edge_server_route(start, goal)
        print(f"Optimal Route from {start} to {goal}: {json.loads(route)}")

        time.sleep(5)  
