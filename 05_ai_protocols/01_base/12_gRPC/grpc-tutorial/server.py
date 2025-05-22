import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        user_id = request.id
        if user_id == 1:
            user = user_pb2.User(
                id=1,
                name="John Doe",
                email="john@example.com"
            )
            return user_pb2.GetUserResponse(user=user)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return user_pb2.GetUserResponse()

    def ListUsers(self, request, context):
        # Simulate a list of users
        users = [
            user_pb2.User(id=1, name="John Doe", email="john@example.com"),
            user_pb2.User(id=2, name="Jane Smith", email="jane@example.com"),
        ]
        return user_pb2.ListUsersResponse(users=users)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()