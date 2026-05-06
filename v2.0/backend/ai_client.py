import httpx
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv("/workspace/projects/.env")


async def analyze_medical(symptoms: str, medical_history: str = "") -> dict:
    """
    调用豆包 (Doubao) API 进行病情分析
    使用官方 v3 Responses API
    """
    api_key = os.getenv("DOUBAO_API_KEY", "")
    
    if not api_key:
        return {
            "diagnosis": "AI 分析暂时不可用（未配置 API Key）",
            "treatment": "请配置豆包 API Key"
        }
    
    api_base = "https://ark.cn-beijing.volces.com/api/v3"
    model = "doubao-seed-2-0-pro-260215"
    
    prompt = f"""你是一位经验丰富的医生。请根据以下信息进行分析：

患者症状：{symptoms}
病史：{medical_history if medical_history else "无"}

请给出：
1. 可能疾病诊断
2. 推荐治疗方案
3. 注意事项

注意：这是辅助诊断，最终诊断请以专业医生为准。"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{api_base}/responses",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": model,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析 v3 API 响应格式
                diagnosis = ""
                treatment = ""
                
                if "output" in data:
                    for item in data["output"]:
                        if item.get("type") == "message":
                            content = item.get("content", [])
                            for c in content:
                                if c.get("type") == "output_text":
                                    full_text = c.get("text", "")
                                    
                                    # 按 markdown 标题分割
                                    if "## 2. 推荐治疗方案" in full_text:
                                        parts = full_text.split("## 2. 推荐治疗方案")
                                        diagnosis = parts[0] if parts else full_text
                                        treatment = "## 2. 推荐治疗方案" + (parts[1] if len(parts) > 1 else "")
                                    elif "## 1. 可能疾病" in full_text:
                                        diagnosis = full_text[:800]
                                        treatment = full_text[800:]
                                    else:
                                        diagnosis = full_text[:800]
                                        treatment = full_text[800:] if len(full_text) > 800 else ""
                
                if diagnosis or treatment:
                    return {
                        "diagnosis": diagnosis[:800] if diagnosis else "分析完成",
                        "treatment": treatment[:800] if treatment else ""
                    }
                else:
                    return {
                        "diagnosis": "AI 响应格式解析失败",
                        "treatment": "请查看完整报告"
                    }
            else:
                error_msg = response.text
                return {
                    "diagnosis": "AI 分析失败",
                    "treatment": f"错误信息: {error_msg}"
                }
    except Exception as e:
        return {
            "diagnosis": "AI 分析失败",
            "treatment": f"连接错误: {str(e)}"
        }
