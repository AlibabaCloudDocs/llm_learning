import dashscope
def sample_call_streaming(prompt_text):
    response_generator = dashscope.Generation.call(
        model='qwen-turbo',
        prompt=prompt_text,
        stream=True,
        top_p=0.8)
    # When stream=True, the return is Generator,
    # need to get results through iteration
    head_idx = 0
    for response in response_generator:
        paragraph = response.output['text']
        print("\r%s" % paragraph[head_idx:len(paragraph)], end='')
        if(paragraph.rfind('\n') != -1):
            head_idx = paragraph.rfind('\n') + 1
