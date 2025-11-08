from transformers import AutoModelForCausalLM, AutoTokenizer
import yaml

def define(public_path : str = "./config/public_config.yaml"):

    try:
        with open(public_path, "r", encoding="utf-8") as f:
            userInfo =  yaml.safe_load(f)
    except:
        raise "사용자 정보가 없습니다. private_config.yaml 파일을 만들어 주세요."
    model_name = userInfo["modelname"]

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype="auto",
        device_map="cpu",
        low_cpu_mem_usage=True  # CPU에서 로딩 최적화
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("모델 loading 완료.......")
    return model , tokenizer


def infer(model, tokenizer , text):

    prompt = f'''  
            예제1. 질문 : 12월 11일 오전 3시 013 열차 부산에서 서울로 가는 열차  답변 : 2025-12-11 03 부산 서울 013
            예제2. 질문 : 4월 3일 오후 11시 1053번 열차 서울에서 부산으로 가는 열차  답변 : 2025-04-03 23 서울 부산 1053
            예제3. 질문 : 1993년 1월 1일 오후 12시 천안 > 서울 546번 열차 답변 : 1993-01-01 12 천안 서울 546
            예제4. 질문 : 2011년 11월 07일 오후 8시 울산 출발 광명 도착 103 열차 답변 : 2011-11-07 20 울산 광명 103
            예제5. 질문 : 4월 2일 오후 10시 052 열차 여수 > 대구 기차 답변 : 2025-04-02 22 여수 대구 052
            
            질문 : {text} 답변 : 
        '''
    messages = [
        {"role": "system", "content": ""},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response