import grpc
import user_pb2
import user_pb2_grpc

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)

        # Test GetUser
        print("Testing GetUser:")
        request = user_pb2.GetUserRequest(id=1)
        try:
            response = stub.GetUser(request)
            if response.user.id:
                print(f"User found: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}")
            else:
                print("User not found")
        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

        # Test ListUsers
        print("\nTesting ListUsers:")
        request = user_pb2.ListUsersRequest()
        try:
            response = stub.ListUsers(request)
            for user in response.users:
                print(f"User: ID={user.id}, Name={user.name}, Email={user.email}")
        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

if __name__ == "__main__":
    main()