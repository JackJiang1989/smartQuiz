from google import genai
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import markdown
import re
# from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()  # 加载 .env 文件
api_key = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=api_key)
# Initialize Google Gemini
# client = genai.Client(api_key="AIzaSyBL5-NfWUKmhamRpnO7OEiMPx2T8bGcaFs")

# Set up app and OpenAI key
app = FastAPI()

# Serve templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Landing page
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# def unwrap_li_paragraphs(html: str) -> str:
#     soup = BeautifulSoup(html, "html.parser")
#     for p in soup.select("li > p"):
#         p.unwrap()  # remove <p> but keep the content
#     return str(soup)


# Handle form submission

# Define the endpoint to generate quiz
@app.post("/generate", response_class=HTMLResponse)
async def post_form(request: Request, country: str = Form(...), subject: str = Form(...), grade: int = Form(...), difficulty: str = Form(...), time: str = Form(...),  language: str = Form(...)):
    #     - The user also has chosen a translation Language (optional): "{language}", If translation Language (optional) is "None", nothing need to be translated. If translation Language (optional) is not "None", provide each question and answer with a **line-by-line translation** into {language} underneath the original.
    # Define the dynamic prompt using user input
    prompt = f"""
    You are a professional quiz generator for educators worldwide.

    Please generate a quiz based on the following parameters:
    - Country: {country}
    - Subject: {subject}
    - Grade Level: Grade {grade}
    - Difficulty: {difficulty}
    - Time: {time}
    - Translation Language (optional): {language if language else 'None'}

    ---

    ## Output Rules & Structure:

    1. **Language Use**:
    - Use the official/native language of {country} as the output language.
    """

    if language:
        prompt += f"""
        - Additionally, provide a translation of both the question and the answer into {language}, placed **immediately after** the original content.
        - Use this structured format:
            - For each question or section:
                - First write it in the official/native language of {country}.
                - Then, on the next line or paragraph, write the translated version in {language}, prefixed by "**[Translation in {language}]**".
        - Keep the structure consistent and easy to follow.
    """
    
    prompt += f"""

    2. **Question Types and Format**:
    The quiz must include **at least three distinct types of questions** suitable for the subject and grade level. 
    Number of the question for each section should be depending on the time from the form: {time}, so the total time for the quiz should be around {time}.

    - For **Mathematics**:
        Section 1 - Fill in the blank to test:
        - Basic arithmetic and calculation

        section 2 - Multiple choice include to test:
        - Unit conversion
        - Rational vs. irrational numbers
        - Fractions and decimals
        - Functions and equations
        - Geometry and spatial reasoning

        section 3 - Problem solving Real-world applications to test:
        - the comprehensive capabilities of the above section1/2.

        section 4 - if {difficulty} is hard, prepare a more advanced open question:

    - For **Languages (Swedish, English, or Chinese)**:
        Section 1 - Fill in the blank to test:
        - Vocabulary

        section 2 - Multiple choice test:
        - Vocabulary usage
        - Grammar correction or transformation
        - Sentence rearrangement or editing

        section 3 - Reading comprehension, it can be but not limited to:
        - given a text, answer questions about it.
        - after the answer questions, ask the user to summarize the text.
        - after summarizing, ask the user to write a short paragraph or essay about the text.

        section 4 - Writing, it can be but not limited to:
        - Short writing prompts (e.g., story beginning)
        - Given a topic, write a short paragraph or essay.

    - For **Science**, include topics such as:
        - Observation and experiment interpretation
        - Understanding scientific concepts (e.g., forces, life cycles, atoms, ecosystems)
        - Application questions linking science to real life
        - Data interpretation or diagrams

    - For **History**, include:
        - Understanding historical events, timelines, and figures
        - Cause and effect relationships
        - Analyzing historical sources (texts or images)
        - Comparison between periods or societies

    **Key goal**: Adapt the question types and focus areas depending on the subject, grade, and country. Ensure the quiz evaluates both conceptual understanding and practical application.

    3. **Content Alignment**:
    Ensure that all questions are grade-appropriate and relevant to the {subject} curriculum of Grade {grade} in {country}. Cover diverse subtopics.

    4. **Randomization & Uniqueness**:
    Make each quiz output **unique**:
    - Randomly select subtopics.
    - Vary question phrasing and examples.
    - Use different names, contexts, or values per request.
    - Do not repeat wording across quizzes.

    5. **Output Structure**:
    - 📌 Use **section icons** like ✏️, 📚, 🧠, ✅ to make the quiz more visually engaging.
    Divide your output into two printable A4 pages:

    ### Page 1: Problem Set
    - Title: "Quiz – {subject}, Grade {grade} – {difficulty}"
    - Questions:
        - Section 1:...
        - Section 2:... 
        - Section 3:...
        ...
    - Number each question clearly.
    - **Do not include answers on this page**.

    ### Page 2: Answer Key
    - Title: "Answer Key – {subject}, Grade {grade}"
    - List correct answers for each question by number.
    - For problem-solving, provide clear steps or explanation.

    6. **Formatting for A4 Export**:
    - Use concise spacing and line lengths to ensure both pages fit A4 without overflowing.
    - Use bullet points or numbering consistently.
    - Avoid excessive whitespace or long texts.

    Generate your output now based on these rules.
    """

    # # Make the API call to Google Gemini (GenAI)
    # try:
    #     response = client.models.generate_content(
    #         model="gemini-2.0-flash",
    #         contents=[prompt]
    #     )
    #     quiz = response.text.strip()  # Extract the generated quiz
    # except Exception as e:
    #     quiz = f"Error: {e}"

    # # Return the quiz response, rendering the HTML page with the results
    # return templates.TemplateResponse("index.html", {"request": request, "quiz": quiz, "country": country, "subject": subject, "grade": grade, "difficulty": difficulty})

    # After getting the response
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        raw_quiz = response.text.strip()
    except Exception as e:
        raw_quiz = f"Error: {e}"

    # pattern = r'(Page ?\d+:|Section ?1:|Sektion ?1:)'
    # pattern1 = re.compile(r'^(Section|Sektion) \d+:$') 
    # data = re.split(pattern, raw_quiz.strip())

    # # 要获取所有 Section 1: 加上后面一句内容
    # results = []
    # i = 0
    # while i < len(data):
    #     item = data[i]
    #     if isinstance(item, str) and pattern1.match(item.strip()):
    #         section_title = '✏️ **'+item.strip()
    #         next_content = data[i + 1] if i + 1 < len(data) else ""
    #         combined = section_title + next_content
    #         results.append(combined)
    #         i += 2  # skip next item
    #     else:
    #         i += 1
    # problem_md = results[0].strip()
    # answer_md = results[1].strip()  

    # problem_html = markdown.markdown(problem_md)
    # answer_html = markdown.markdown(answer_md)

    # 1. 正则表达式匹配分页与小节标题
    split_pattern = r'(Page ?\d+:|Section ?1:|Sektion ?1:)'
    section_pattern = re.compile(r'^(Section|Sektion) 1:$')

    # 2. 分割原始文本
    parts = re.split(split_pattern, raw_quiz.strip())

    # 3. 重组为带前缀的内容块
    chunks = []
    for i in range(1, len(parts), 2):  # 从索引1开始，每两个为一组
        prefix = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ''
        chunks.append(f"{prefix} {content}")

    # 4. 提取 Section/Sektion 1 内容并加上图标
    section_1_chunks = []
    for chunk in chunks:
        if section_pattern.match(chunk.split()[0] + ' ' + chunk.split()[1]):
            section_1_chunks.append(f"✏️ **{chunk}**")

    # 5. 提取问题和答案部分（默认第一个为题目，第二个为答案）
    problem_md = section_1_chunks[0].strip() if len(section_1_chunks) > 0 else ""
    answer_md = section_1_chunks[1].strip() if len(section_1_chunks) > 1 else ""

    # 6. 转换为 HTML
    problem_html = markdown.markdown(problem_md)
    answer_html = markdown.markdown(answer_md)

    # 处理 HTML，去掉 在<li>里面<p>标签防止换行
    # soup = BeautifulSoup(html, "html.parser")

    # # Loop through all <li> tags
    # for li in soup.find_all("li"):
    #     p = li.find("p")
    #     if p:
    #         # Replace the <p> with its inner content
    #         p.unwrap()

    # split_match = re.split(r'(Page 2:)', raw_quiz.strip(), maxsplit=1)
    # if len(split_match) >= 3:
    #     problem_md = split_match[0].strip()
    #     answer_md = (split_match[1] + split_match[2]).strip()  # re-add "Page 2:" prefix
    # else:
    #     problem_md = raw_quiz.strip()
    #     answer_md = ""


    return templates.TemplateResponse("index.html", {
        "request": request,
        "quiz_problem": problem_html,
        "quiz_answer": answer_html,
        "country": country,
        "subject": subject,
        "grade": grade,
        "time" : time,
        "difficulty": difficulty
    })



# prompt rev.0

# f"""
#     You are a professional quiz generator for educators worldwide.

#     Please generate a quiz based on the following parameters:
#     - Country: {country}
#     - Subject: {subject}
#     - Grade Level: Grade {grade}
#     - Difficulty: {difficulty}
#     - Translation Language (optional): {language if language else "None"}

#     ---

#     ## Output Rules & Structure:

#     1. **Language Use**:
#     - Use the official/native language of {country} as the primary language.
#     - If the translation language is not None, provide each question and answer with a **line-by-line translation** into {language} underneath the original.

#     2. **Question Types**:
#     The quiz must include **at least three distinct types of questions** suitable for the subject and grade level. Do not rigidly stick to a fixed format; instead, use your best judgment to vary the format and structure to enhance engagement and test understanding.

#     - For **Mathematics**, cover a balanced mix from:
#         - Basic arithmetic and calculation
#         - Unit conversion
#         - Rational vs. irrational numbers
#         - Fractions and decimals
#         - Functions and equations
#         - Geometry and spatial reasoning
#         - Real-world applications and word problems

#     - For **Languages (Swedish, English, or Chinese)**, draw from:
#         - Reading comprehension
#         - Cloze (fill-in-the-blank for grammar or vocabulary)
#         - Vocabulary usage
#         - Grammar correction or transformation
#         - Short writing prompts (e.g., story beginning)
#         - Sentence rearrangement or editing

#     - For **Science**, include topics such as:
#         - Observation and experiment interpretation
#         - Understanding scientific concepts (e.g., forces, life cycles, atoms, ecosystems)
#         - Application questions linking science to real life
#         - Data interpretation or diagrams

#     - For **History**, include:
#         - Understanding historical events, timelines, and figures
#         - Cause and effect relationships
#         - Analyzing historical sources (texts or images)
#         - Comparison between periods or societies

#     **Key goal**: Adapt the question types and focus areas depending on the subject, grade, and country. Ensure the quiz evaluates both conceptual understanding and practical application.


#     3. **Content Alignment**:
#     Ensure that all questions are grade-appropriate and relevant to the {subject} curriculum of Grade {grade} in {country}. Cover diverse subtopics.

#     4. **Randomization & Uniqueness**:
#     Make each quiz output **unique**:
#     - Randomly select subtopics.
#     - Vary question phrasing and examples.
#     - Use different names, contexts, or values per request.
#     - Do not repeat wording across quizzes.

#     5. **Output Structure**:
#     Divide your output into two printable A4 pages:

#     ### Page 1: Problem Set
#     - Title: "Quiz – {subject}, Grade {grade} – {difficulty}"
#     - Format:
#         - Section 1: Fill-in-the-Blank
#         - Section 2: Multiple Choice
#         - Section 3: Problem Solving
#     - Number each question clearly.
#     - **Do not include answers on this page**.

#     ### Page 2: Answer Key
#     - Title: "Answer Key – {subject}, Grade {grade}"
#     - List correct answers for each question by number.
#     - For problem-solving, provide clear steps or explanation.

#     6. **Formatting for A4 Export**:
#     - Use concise spacing and line lengths to ensure both pages fit A4 without overflowing.
#     - Use bullet points or numbering consistently.
#     - Avoid excessive whitespace or long texts.

#     7. **Output Example** (use as guide, don't repeat exactly):
#     - Q1. Fill in the blank: "The capital of France is ____."  
#         [Translation: "法国的首都是 ____。"]
#     - A1: Paris

#     Generate your output now based on these rules.
#     """