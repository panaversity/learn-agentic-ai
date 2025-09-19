# Self-hosting Llama 4 Maverick on Kubernetes

Since you’re specifically asking about self-hosting Llama 4 Maverick on Kubernetes with a focus on the most economical option, let’s tailor the approach based on the details available as of April 6, 2025. Meta announced Llama 4 on April 5, 2025, with Llama 4 Maverick being one of the initial releases. It’s a multimodal model with 17 billion active parameters, 128 experts, and 400 billion total parameters, built on a Mixture of Experts (MoE) architecture, which makes it more compute-efficient than dense models. This efficiency can help reduce hosting costs, but its size and multimodal capabilities (text and image processing) still demand significant resources. Here’s how to optimize for cost on Kubernetes.

### Llama 4 Maverick Requirements
- **Model Size**: With 400B total parameters, the memory footprint depends on precision and MoE efficiency. Only 17B parameters are active per token, but the full model must reside in memory or storage. Assuming FP16 (16-bit) precision, the total model weights are ~800GB unquantized. However, MoE reduces active memory use per inference to ~34GB (17B × 2 bytes), plus overhead (context, activations). Quantization (e.g., 4-bit) could shrink this further.
- **Quantized Estimate**: Using 4-bit quantization (like AWQ or GPTQ), the total model might compress to ~200GB, with active inference needing ~10-12GB VRAM per request, making it feasible on smaller GPUs.
- **Multimodal Overhead**: Image processing adds complexity, likely requiring 2-4GB extra VRAM per request, depending on input resolution.
- **Inference Engine**: Tools like vLLM or llama.cpp with MoE support can optimize memory and throughput.

### Most Economical Self-Hosting Strategy
To minimize costs on Kubernetes, focus on low-cost hardware, efficient resource use, and cloud spot instances with serverless scaling. Here’s the breakdown:

#### 1. Hardware Choice: Single NVIDIA A40 or T4 with Quantization
- **Why**: Llama 4 Maverick’s MoE design means only a fraction of parameters are active, so a single GPU can handle it with quantization. An NVIDIA A40 (48GB VRAM) supports 4-bit quantization (~200GB model fits with swapping to RAM/SSD, active inference ~12-16GB VRAM). Alternatively, a T4 (16GB VRAM) works for minimal workloads with aggressive quantization and offloading.
- **Cost**:
  - **T4 Spot**: ~$0.08-$0.15/hour (AWS/GCP).
  - **A40 Spot**: ~$0.80-$1.00/hour (AWS/GCP).
- **Tradeoff**: T4 is cheaper but slower (5-10 tokens/s); A40 offers 20-30 tokens/s and multimodal support.

#### 2. Quantization: 4-bit for Memory Efficiency
- Use 4-bit quantization (e.g., AWQ) to fit the model on a single GPU. This reduces VRAM from ~800GB (FP16) to ~200GB total, with active inference fitting in 12-16GB. Tools like vLLM support MoE and quantization, minimizing quality loss while slashing hardware needs.

#### 3. Kubernetes Setup: Spot Instances + Serverless
- **Cloud Provider**: GCP or AWS for spot/preemptible instances.
  - **GCP Preemptible T4**: $0.11/hour.
  - **AWS Spot A40**: $0.80/hour.
- **Managed Kubernetes**: 
  - **GKE**: Free control plane, ~$0.10/hour base cost with Autopilot (pay-per-pod).
  - **EKS**: $0.10/hour base + EC2 spot costs.
- **Serverless**: Use KServe or Knative to scale to zero when idle, avoiding idle GPU costs. Only pay for active inference time.
- **Autoscaling**: Configure Horizontal Pod Autoscaler (HPA) on GPU utilization (e.g., 70%) to spin up pods only as needed.

#### 4. Storage Optimization
- **Model Weights**: Store the ~200GB quantized model on a cheap SSD (e.g., AWS EBS, $0.02/GB/month = $4/month). Use PersistentVolumeClaims (PVCs) in Kubernetes.
- **Caching**: Preload weights into RAM or NVMe for faster startup, but SSD suffices for cost.

#### 5. Inference Engine: vLLM
- **Why**: vLLM supports MoE, quantization, and tensor parallelism, maximizing throughput (e.g., 30 tokens/s on A40). It’s OpenAI API-compatible, simplifying integration.
- **Config**: `--model meta-llama/Llama-4-Maverick --quantization awq --gpu-memory-utilization 0.95`.

### Cost Breakdown (A40 Spot on AWS EKS)
- **Compute**: $0.80/hour × 730 hours = $584/month (24/7).
- **Kubernetes**: $0.10/hour × 730 = $73/month.
- **Storage**: $4/month.
- **Total (24/7)**: ~$661/month.
- **Serverless Savings**: With KServe scaling to zero, costs drop to $73/month (EKS base) + usage (e.g., $0.80/hour × 50 hours = $40/month), totaling ~$113/month for light use.

### Cheapest Option: T4 Spot on GKE
- **Compute**: $0.11/hour × 730 = $80/month (24/7).
- **GKE**: Free control plane, ~$0.05/hour node cost = $36/month.
- **Storage**: $4/month.
- **Total (24/7)**: ~$120/month.
- **Serverless**: ~$40/month (base + light usage).

### Comparison to Hosted Services
- **Groq**: $0.50/M input, $0.77/M output tokens (April 5, 2025, groq.com).
- **DeepInfra**: $0.20/M input, $0.60/M output (X posts, April 5, 2025).
- **Self-Hosted**: At 1M tokens/day (~30M/month), T4 setup = $120/month vs. DeepInfra’s $600-$900/month. Break-even is ~200K tokens/day.

### Final Recommendation
The most economical option for self-hosting Llama 4 Maverick on Kubernetes is a single T4 GPU on GCP GKE with 4-bit quantization, spot instances, and KServe for serverless scaling. This costs ~$120/month for 24/7 use or ~$40/month with light traffic, leveraging MoE efficiency and cheap cloud resources. For higher throughput or multimodal needs, swap to an A40 (~$661/month 24/7, ~$113/month serverless), still beating hosted API costs for moderate usage. Adjust based on your token volume—low traffic favors this setup, while heavy use might lean toward hosted services.

## Self-hosting Google Gemma on Kubernetes

Google announced Gemma 3 on March 11, 2025, as a family of lightweight, open-source models built from Gemini 2.0 tech, available in sizes of 1B, 4B, 12B, and 27B parameters. Gemma 3 introduces multimodal capabilities (text and vision) and a 128K-token context window, with improved efficiency over its predecessors. I’ll assume you’re interested in the 12B variant as a balanced choice (similar to Llama 4 Maverick’s mid-tier scale), but I’ll note adjustments for other sizes. Here’s the most economical way to self-host Gemma 3 12B on Kubernetes.

### Gemma 3 12B Requirements
- **Model Size**: 12 billion parameters. At FP16 (16-bit), weights need ~24GB VRAM, plus ~4-6GB for inference overhead (context, activations), totaling ~28-30GB. At 4-bit quantization (e.g., GPTQ), this drops to ~6-8GB VRAM for weights, ~10-12GB total. Vision tasks add ~2-4GB VRAM per request.
- **Compute**: GPU acceleration is ideal; throughput is ~20-30 tokens/s on a mid-tier GPU. CPU offloading works but slows inference (~5-10 tokens/s).
- **Storage**: ~12GB (quantized) to ~24GB (FP16) for weights, downloadable from Hugging Face or Kaggle.

### Most Economical Self-Hosting Strategy
To keep costs low, we’ll use a single affordable GPU, spot instances, quantization, and serverless scaling on Kubernetes. Here’s the plan:

#### 1. Hardware Choice: NVIDIA T4 with Quantization
- **Why**: The T4 (16GB VRAM) is cost-effective and widely available on cloud spot markets. With 4-bit quantization, Gemma 3 12B fits comfortably (~10-12GB VRAM, ~14GB with vision), delivering 20-30 tokens/s for text or 15-20 tokens/s with images. Alternatives like A40 (48GB, $0.80/hour spot) are overkill for this size unless you skip quantization.
- **Cost**:
  - **Spot Price**: ~$0.08-$0.15/hour (AWS g4dn.xlarge) or ~$0.11/hour (GCP preemptible).

#### 2. Quantization: 4-bit for Efficiency
- Use 4-bit quantization via vLLM or Hugging Face `transformers`. This slashes VRAM from ~30GB to ~10-12GB, fitting a T4 while maintaining near-FP16 quality (e.g., <5% performance drop per Google’s Gemma 3 benchmarks). Vision tasks still work with the SigLIP encoder integrated into the 12B+ models.

#### 3. Kubernetes Setup: Spot Instances + Serverless
- **Cloud Provider**: GCP GKE or AWS EKS for cost-effective managed Kubernetes.
  - **GKE**: Free control plane in Autopilot (~$0.05-$0.10/hour base), preemptible T4 at $0.11/hour.
  - **EKS**: $0.10/hour control plane + spot T4 at $0.08-$0.15/hour.
- **Serverless**: Deploy with KServe or Knative to scale to zero when idle, paying only for active inference. Use Horizontal Pod Autoscaler (HPA) on GPU utilization (e.g., 70%) for load spikes.
- **Node Config**: Single T4 GPU, 4 vCPUs, 16GB RAM (e.g., AWS g4dn.xlarge or GCP n1-standard-4 + T4).

#### 4. Storage Optimization
- **Model Weights**: Store the ~12GB quantized model on SSD (e.g., AWS EBS or GCP PD, $0.02/GB/month = $0.24/month). Use Kubernetes PVCs.
- **Caching**: Preload weights into RAM on pod startup for speed, falling back to SSD for cost.

#### 5. Inference Engine: vLLM
- **Why**: vLLM supports Gemma 3’s multimodal inputs (text + vision via SigLIP), quantization, and high throughput. It’s OpenAI API-compatible and efficient on single GPUs.
- **Config**: `--model google/gemma-3-12b --quantization gptq --max-model-len 131072 --gpu-memory-utilization 0.9`.

### Cost Breakdown (T4 Spot on GKE)
- **Compute**: $0.11/hour × 730 hours = $80.30/month (24/7).
- **GKE**: ~$0.05/hour × 730 = $36.50/month.
- **Storage**: $0.24/month.
- **Total (24/7)**: ~$117/month.
- **Serverless Savings**: With KServe, ~$36.50/month (base) + usage (e.g., $0.11/hour × 50 hours = $5.50/month), totaling ~$42/month for light use.

### AWS EKS Alternative
- **Compute**: $0.08/hour × 730 = $58.40/month (24/7).
- **EKS**: $0.10/hour × 730 = $73/month.
- **Storage**: $0.24/month.
- **Total (24/7)**: ~$132/month.
- **Serverless**: ~$73/month (base) + $4/month (light usage) = ~$77/month.

### Size Variants
- **1B**: ~2GB VRAM (4-bit), fits on CPU or T4, ~$40/month serverless on GKE. Text-only, no vision.
- **4B**: ~4-6GB VRAM (4-bit), T4 sufficient, ~$42/month serverless. Vision supported.
- **27B**: ~20-22GB VRAM (4-bit), needs A40 (~$0.80/hour spot), ~$661/month 24/7 or ~$113/month serverless.

### Comparison to Hosted Services
- **Vertex AI**: ~$0.0001/token (March 2025 pricing). At 1M tokens/day (~30M/month), ~$90/month.
- **Self-Hosted**: $42-$117/month beats Vertex for >400K tokens/day.

### Final Recommendation
The most economical option for self-hosting Gemma 3 12B on Kubernetes is a single NVIDIA T4 GPU on GCP GKE with 4-bit quantization, preemptible instances, and KServe for serverless scaling. This costs ~$117/month for 24/7 use or ~$42/month with light traffic (e.g., 50 hours/month), leveraging Gemma 3’s efficiency and single-GPU optimization (Google claims it outperforms Llama-405B on one H100). For minimal needs, the 4B model offers similar savings with vision support, while 27B requires pricier hardware (A40 or H100). Adjust based on your usage—low traffic favors this setup, high traffic may tilt toward hosted APIs.