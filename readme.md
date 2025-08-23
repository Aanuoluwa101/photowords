**PhotoWords 🎮🖼️**
====================

A full-stack, serverless word puzzle game built entirely on AWS. PhotoWords challenges users to deduce a hidden word by combining letter sequences from a set of provided images. This project is a hands-on demonstration of AWS serverless architecture, focusing on scalability, cost-efficiency, and performance.

**🧠 The Concept**
------------------

The core gameplay of PhotoWords is simple yet engaging:

1.  **Present:** Users are shown a set of images (e.g., a **cat**, a **dog**, and a **log**).
    
2.  **Deduce:** Each image has an associated "tag" (its name). Users must select a substring (start and end index) from each tag.
    
3.  **Combine:** The selected substrings are concatenated to form a new word (e.g., **'c'** from **cat** + **'o'** from **dog** + **'g'** from **log** = **'cog'**).
    

This project is less about the game's frontend and more about building a robust, cloud-native backend to support it.

**🏗️ System Architecture & AWS Services**
------------------------------------------

The application is built on a serverless foundation, ensuring there are no constantly running servers, automatic scaling, and a pay-per-use cost model. The architecture is designed for high availability, security, and performance.

[https://imgur.com/a/I3hu7A5](https://imgur.com/a/I3hu7A5)

### **Core Components:**

### **1. Frontend & Content Delivery (Amazon CloudFront)**

*   **Purpose:** Serves the static React.js frontend and cached API responses globally with low latency.
    
*   **Why?:** Provides a fast user experience worldwide and reduces load on backend services. It also simplifies serving the application over HTTPS.
    

### **2. Authentication (Amazon Cognito)**

*   **Purpose:** Handles login and session management for the admin panel.
    
*   **Why?:** Offloads the complex responsibility of user authentication and authorization to a managed service, ensuring security best practices are followed.
    

### **3. API Layer (Amazon API Gateway)**

*   **Purpose:** Creates a secure, managed RESTful API that acts as the single entry point for all client requests.
    
*   **Key Features:**
    
    *   **Request Validation:** Uses JSON schemas to validate request bodies for **CreateGroup**, **GameAttemptCreate**, and **GameAttemptFinish** before invoking Lambda functions, improving security and reducing error handling code.
        
    *   **Authorization:** Integrates with Cognito to protect admin endpoints (e.g., creating/deleting images and image groups).
        
    *   **Throttling:** Protects backend resources from traffic spikes and abuse.
        

### **4\. Business Logic (AWS Lambda)**

*   **Purpose:** Runs stateless code in response to events (API calls, S3 uploads). This is where the core application logic resides.
    
*   **Key Functions & Design Patterns:**
    
    *   **create-game-attempt:** Initiates a new game. Fetches all questions (image groups), shuffles them, and selects a subset. It then writes the attempt to DynamoDB and **caches the entire attempt in Redis for 1 day** to enable fast, stateful gameplay without constant database reads.
        
    *   **finish-game-attempt:** Processes user answers, calculates scores, and updates the attempt status in DynamoDB. It **deletes the cached attempt** from Redis upon completion.
        
    *   **get-groups:** Demonstrates the **Cache-Aside Pattern**. It first checks Redis for groups. On a cache miss, it loads all groups from DynamoDB, caches each one individually in Redis (**group:**), and returns the result. This significantly reduces read latency and database load for frequently accessed data.
        
    *   **get-images:** Returns a list of all available image tags from a Redis Set (**all\_images**), enabling fast lookups for the admin panel.
        
    *   **generate-presigned-url:** Generates a time-limited, secure URL allowing the frontend to upload an image directly to S3 without exposing backend credentials.
        
    *   **register-image:** Triggered by an S3 upload event. It validates the object key, ensures the tag is unique, and writes the metadata to DynamoDB and Redis.
        
    *   **delete-group & delete-image:** Handle deletion, ensuring consistency by removing items from both DynamoDB and Redis cache simultaneously.

    docs at https://documenter.getpostman.com/view/29374610/2sB2j989TW
        

### **5. Data Layer**

*   **Amazon DynamoDB:** A managed NoSQL database used as the system of record.
    
    *   **images table:** Stores metadata for uploaded images (**tag**, **uploaded\_at**).
        
    *   **groups table:** Stores each puzzle question (**id**, **answer**, **difficulty**, **hint**, **images** array).
        
    *   **attempts table:** Stores user game attempts (**id**, **username**, **status**, **answers**, **time\_taken**).
        
    *   **Why DynamoDB?:** Offers single-digit millisecond latency at any scale, a simple pay-per-request model, and seamless integration with Lambda.
        
*   **Amazon ElastiCache for Redis:** A managed in-memory data store used as a performance-optimizing cache.
    
    *   **Cached Data:**
        
        *   **group:**: Entire group JSON objects.
            
        *   **attempt:**: Active game attempts with all questions included.
            
        *   **all\_images**: A Set of all image tags.
            
    *   **Why Redis?:** Provides microsecond read latency, offloading repetitive read operations from DynamoDB and making the game experience snappy. The use of IAM authentication for Redis enhances security.
        

### **6. File Storage (Amazon S3)**

*   **Purpose:** Highly durable object storage for all game images.
    
*   **Why?:** Provides infinite scalability, 99.999999999% durability, and seamless integration with CloudFront for fast distribution. The use of presigned URLs for uploads is a secure best practice.
    

### **7. Networking & Security (Amazon VPC)**

*   **Purpose:** Isolates backend resources (Lambda Functions, ElastiCache) in a private network.
    
*   **Key Components:**
    
    *   **Private Subnet:** Lambda functions that need to access ElastiCache are deployed into a VPC's private subnet for secure networking.
        
    *   **VPC Endpoint for S3 (Gateway Endpoint):** Allows Lambda functions in the VPC to access S3 buckets **without traversing the public internet**. This is a crucial security and performance enhancement.
        
    *   **Security Groups:** Act as firewalls to control traffic at the instance and subnet level, respectively, ensuring only authorized communication is allowed.
        

**⚙️ Key Technical Decisions & Justifications**
-----------------------------------------------

1.  **Serverless First:**
    
    *   **Why?** Maximizes sc alability and cost-efficiency. We only pay for the compute time we consume (Lambda) and the resources we use (DynamoDB, S3). There is no operational overhead of managing servers.
        
2.  **Redis as a Cache (Cache-Aside Pattern):**
    
    *   **Why?** DynamoDB is fast, but in-memory caching is orders of magnitude faster. Caching game attempts (**attempt:**) is essential for a smooth, real-time gameplay experience without introducing noticeable latency from database reads on every guess.
        
3.  **VPC Endpoints for Private Connectivity:**
    
    *   **Why?** While Lambda functions can access public services like S3 via the internet, this is less secure and can be slower. Using a **VPC Gateway Endpoint for S3** provides a private, secure, and highly reliable connection within the AWS network backbone, improving both security and performance while lowering operational costs by **bypassing the need for a costly NAT Gateway.**
        
4.  **IAM Authentication for Redis:**
    
    *   **Why?** Instead of traditional password-based authentication, the Lambda functions use IAM roles to generate secure temporary credentials to connect to Redis. This is more secure and eliminates the need to manage and rotate secrets manually.
        
5.  **Presigned URLs for S3 Uploads:**
    
    *   **Why?** It allows the frontend to upload directly to S3 without proxying through a backend service (API Gateway + Lambda). This is more efficient, scalable, and secure, as the backend never handles the binary image data.
        

**🚀 Deployment**
-----------------

The infrastructure is defined as code using AWS CDK or Terraform. The **infrastructure/** directory contains the stacks to deploy:

1.  VPC with public and private subnets
    
2.  DynamoDB Tables
    
3.  ElastiCache Redis Cluster
    
4.  S3 Bucket
    
5.  Lambda Functions with appropriate IAM roles and VPC configurations
    
6.  API Gateway with routes and Cognito authorizer
    
7.  Cognito User Pool
    

**🔮 Future Enhancements**
--------------------------

*   **Secrets & Configuration Management:** Migrate from Lambda environment variables to **AWS Systems Manager Parameter Store**. This would provide a more secure, centralized, and auditable method for managing configuration (e.g., table names) and secrets (e.g., Redis credentials), supporting versioning and fine-grained access control.