import grpc
from concurrent import futures
import vehicle_edge_pb2
import vehicle_edge_pb2_grpc
import cv2
import numpy as np
import torch
import json
from route_planning import a_star  

# YOLOv5 model (using for object detection)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)

class EdgeServer(vehicle_edge_pb2_grpc.EdgeServerServicer):
    def ProcessImage(self, request, context):
        nparr = np.frombuffer(request.image, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        detected_objects = self.detect_objects(img)
        return vehicle_edge_pb2.ImageResponse(result=detected_objects)

    def detect_objects(self, img):
        results = model(img)
        detected_objects = results.pandas().xyxy[0]  
        print("Detected Objects:", detected_objects)
        return detected_objects.to_json(orient="records")  
    def PlanRoute(self, request, context):
        graph = {
            'A': [('B', 1), ('C', 3)],
            'B': [('A', 1), ('D', 1)],
            'C': [('A', 3), ('D', 1)],
            'D': [('B', 1), ('C', 1)]
        }
        path = a_star(graph, request.start, request.goal)
        return vehicle_edge_pb2.RouteResponse(path=json.dumps(path))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vehicle_edge_pb2_grpc.add_EdgeServerServicer_to_server(EdgeServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Edge Server started on port 50051.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
