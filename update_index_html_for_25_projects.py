import os

base_dir = "/Users/abhi/Documents/Antigravity"
index_path = os.path.join(base_dir, "index.html")

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update stats in hero
content = content.replace("20 Production-Grade Architectures", "25 Production-Grade Architectures")
content = content.replace("20 Architectural Blueprints", "25 Architectural Blueprints")
content = content.replace("250 / 250 Tests Passed", "310 / 310 Tests Passed")
content = content.replace("250 Tests Passed", "310 Tests Passed")
content = content.replace("20 Architectural Blueprints with 2D Flowcharts", "25 Architectural Blueprints with 2D Flowcharts")
content = content.replace("20 Enterprise Projects", "25 Enterprise Projects")

p21_25_cards = """
        <!-- 21 -->
        <div class="project-card">
            <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/21-vllm-multi-lora-dynamic-serving" class="card-main-link" target="_blank">
                <div class="project-num">PROJECT 21</div>
                <div class="project-title">vLLM Multi-LoRA Dynamic Serving &rarr;</div>
                <div class="project-desc">Multi-tenant LoRA adapter dynamic hot-swapping and LRU cache management on a single base model, executed via fused Segmented GEMM kernels.</div>
                <div class="tags">
                    <span class="tag">Multi-LoRA</span>
                    <span class="tag">Segmented GEMM</span>
                    <span class="tag">vLLM / S-LoRA</span>
                </div>
            </a>
            <div class="project-footer">
                <div class="test-status">12 / 12 Passed</div>
                <div class="links-group">
                    <a href="21-vllm-multi-lora-dynamic-serving/FLOWCHART.html" class="flowchart-link" target="_blank">Flowchart 🔀</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/21-vllm-multi-lora-dynamic-serving/PROD_ARCHITECTURE_REASONING.md" class="reasoning-link" target="_blank">Blueprint &rarr;</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/21-vllm-multi-lora-dynamic-serving" class="code-link" target="_blank">Code &rarr;</a>
                </div>
            </div>
        </div>

        <!-- 22 -->
        <div class="project-card">
            <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/22-disaggregated-prefill-decode-engine" class="card-main-link" target="_blank">
                <div class="project-num">PROJECT 22</div>
                <div class="project-title">Disaggregated Prefill vs. Decode &rarr;</div>
                <div class="project-desc">Splitwise / Mooncake disaggregated serving architecture separating compute-heavy prompt prefill from memory-bound decode with GPUDirect RDMA KV transfer.</div>
                <div class="tags">
                    <span class="tag">Disaggregated</span>
                    <span class="tag">Mooncake / Splitwise</span>
                    <span class="tag">RDMA KV Pool</span>
                </div>
            </a>
            <div class="project-footer">
                <div class="test-status">12 / 12 Passed</div>
                <div class="links-group">
                    <a href="22-disaggregated-prefill-decode-engine/FLOWCHART.html" class="flowchart-link" target="_blank">Flowchart 🔀</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/22-disaggregated-prefill-decode-engine/PROD_ARCHITECTURE_REASONING.md" class="reasoning-link" target="_blank">Blueprint &rarr;</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/22-disaggregated-prefill-decode-engine" class="code-link" target="_blank">Code &rarr;</a>
                </div>
            </div>
        </div>

        <!-- 23 -->
        <div class="project-card">
            <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/23-fp8-mixed-precision-gemm-engine" class="card-main-link" target="_blank">
                <div class="project-num">PROJECT 23</div>
                <div class="project-title">Native FP8 Mixed-Precision GEMM &rarr;</div>
                <div class="project-desc">NVIDIA Hopper H100 native FP8 Tensor Core acceleration (E4M3/E5M2) with dynamic delayed scaling calibration and zero perplexity degradation.</div>
                <div class="tags">
                    <span class="tag">FP8 GEMM</span>
                    <span class="tag">Hopper H100</span>
                    <span class="tag">Delayed Scaling</span>
                </div>
            </a>
            <div class="project-footer">
                <div class="test-status">12 / 12 Passed</div>
                <div class="links-group">
                    <a href="23-fp8-mixed-precision-gemm-engine/FLOWCHART.html" class="flowchart-link" target="_blank">Flowchart 🔀</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/23-fp8-mixed-precision-gemm-engine/PROD_ARCHITECTURE_REASONING.md" class="reasoning-link" target="_blank">Blueprint &rarr;</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/23-fp8-mixed-precision-gemm-engine" class="code-link" target="_blank">Code &rarr;</a>
                </div>
            </div>
        </div>

        <!-- 24 -->
        <div class="project-card">
            <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/24-nccl-distributed-collective-profiler" class="card-main-link" target="_blank">
                <div class="project-num">PROJECT 24</div>
                <div class="project-title">NCCL Collective Communication Profiler &rarr;</div>
                <div class="project-desc">Profiles multi-GPU collective communication bandwidth (All-Reduce, All-Gather), detecting straggler GPU ranks and analyzing NVLink / RoCE network saturation.</div>
                <div class="tags">
                    <span class="tag">NCCL Profiler</span>
                    <span class="tag">Straggler Ranks</span>
                    <span class="tag">NVLink Saturation</span>
                </div>
            </a>
            <div class="project-footer">
                <div class="test-status">12 / 12 Passed</div>
                <div class="links-group">
                    <a href="24-nccl-distributed-collective-profiler/FLOWCHART.html" class="flowchart-link" target="_blank">Flowchart 🔀</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/24-nccl-distributed-collective-profiler/PROD_ARCHITECTURE_REASONING.md" class="reasoning-link" target="_blank">Blueprint &rarr;</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/24-nccl-distributed-collective-profiler" class="code-link" target="_blank">Code &rarr;</a>
                </div>
            </div>
        </div>

        <!-- 25 -->
        <div class="project-card">
            <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/25-speculative-medusa-multi-head-verifier" class="card-main-link" target="_blank">
                <div class="project-num">PROJECT 25</div>
                <div class="project-title">Medusa Multi-Head Speculation &rarr;</div>
                <div class="project-desc">Accelerates generation up to 2.85x by predicting multiple candidate tokens with attached MLP heads and verifying them in parallel using 2D Tree Attention masks.</div>
                <div class="tags">
                    <span class="tag">Medusa</span>
                    <span class="tag">Tree Attention</span>
                    <span class="tag">Speculative Decoding</span>
                </div>
            </a>
            <div class="project-footer">
                <div class="test-status">12 / 12 Passed</div>
                <div class="links-group">
                    <a href="25-speculative-medusa-multi-head-verifier/FLOWCHART.html" class="flowchart-link" target="_blank">Flowchart 🔀</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/25-speculative-medusa-multi-head-verifier/PROD_ARCHITECTURE_REASONING.md" class="reasoning-link" target="_blank">Blueprint &rarr;</a>
                    <a href="https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/25-speculative-medusa-multi-head-verifier" class="code-link" target="_blank">Code &rarr;</a>
                </div>
            </div>
        </div>
"""

# Insert before `</div>\n\n    <footer>`
if "<!-- 20 -->" in content and "<!-- 21 -->" not in content:
    target_split = content.split("<!-- 20 -->")
    # find closing div for project 20
    card_20_part = target_split[1]
    end_of_20 = card_20_part.find("</div>\n        </div>") + len("</div>\n        </div>")
    
    updated_content = target_split[0] + "<!-- 20 -->" + card_20_part[:end_of_20] + p21_25_cards + card_20_part[end_of_20:]
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("Successfully updated index.html with Projects 21 to 25!")
else:
    print("Cards 21-25 already present or split point not found.")
