import streamlit as st
from tkinter import filedialog
import concurrent.futures as cf
import streamlit_antd_components as sac
import os

# 定义样式
def style():
    st.html("""<style>
            /* Header的样式 */
            [data-testid="stHeader"] {
                height: 1px;
            }

            /* body的样式--边距 */
            [data-testid="stAppViewBlockContainer"] { 
                padding: 50px 50px;
            }


            /* 侧边栏Header的样式--边距高度 */
            [data-testid="stSidebarHeader"] {
                padding: 10px 0px;
                height: 0px;
            }

            /* 侧边栏Content的样式--外边距 */
            [data-testid="stSidebarUserContent"] { 
                padding: 0px 13px;
            }

        </style>
        <script>
        document.getElementById("return-to-top").addEventListener("click", function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
        </script>
        """)

# 用tkinter获取文件路径
def get_file_paths():
        file_paths = filedialog.askopenfilenames(title="选择HTML文件或txt文件", filetypes=[("HTML文件", "*.html;*.txt")])
        return file_paths

# 进程池执行tkinter函数
def threadpool():
    # 创建进程池执行器
    with cf.ProcessPoolExecutor() as executor:
    # 启动进程执行任务
        futures = executor.submit(get_file_paths)
        result = futures.result()
    return result

# 分页形式显示选取的文件名称
def show_file_names(file_paths):
    # 提取父目录
    parent_dir = os.path.dirname(file_paths[0])
    # 提取文件名
    file_names = [file_path.split("/")[-1] for file_path in file_paths]
    # 分页显示列表名称
    # 分页配置
    page_size = 10  # 每页显示的文件数量
    total_items = len(file_names)  # 文件总数
    
    if "curpage_m" not in st.session_state:
        st.session_state.curpage_m = 1

    if "current_page_m" not in st.session_state:
        st.session_state["current_page_m"] = 1
    else:
        st.session_state["current_page_m"] = st.session_state.curpage_m
    # 当前页码
    current_page = st.session_state.current_page_m
    file_names_page = file_names[page_size * (current_page - 1):page_size * current_page]

    sac.pagination(total=total_items, page_size=page_size, align='center',
                jump=True, show_total=True, key='curpage_m')
    
    file_name_select = sac.menu(file_names_page,index=0,variant="left-bar")
    return file_name_select, parent_dir


# 侧边栏设置项
def sidebar_setting():
    side = st.sidebar
    with side.expander("设置"):
        # 用户可以通过滑块选择行间距
        line_height = st.slider('选择行间距 (倍数)', 1.0, 3.0, 2.0)

        # 样式选择方案
        color_scheme = st.radio("选择颜色方案", ("白底黑字", "黑底白字","选择器选择"), index=0,horizontal=True)
        # 按照颜色方案设置css样式
        if color_scheme == "白底黑字" or color_scheme == "黑底白字":
            # 颜色方案
            text_color = 'white' if color_scheme == '黑底白字' else 'black'
            background_color = 'black' if color_scheme == '黑底白字' else 'white'
   
            
        elif color_scheme == "选择器选择":
            # 用户可以通过颜色选择器选择背景颜色
            background_color = st.color_picker('选择背景颜色', '#89AF4C')

            # 用户通过颜色选择器选择字体颜色
            text_color = st.color_picker('选择字体颜色', '#000000')

        # 用户可以通过滑块选择文字大小
        font_size = st.slider('选择文字大小', 10, 30, 20)

        # 用户可以通过复选框选择是否加粗
        bold_text = st.checkbox('加粗文字')

    # 生成CSS样式字符串
    
    # 字体加粗设置
    bold_style = "font-weight: bold;" if bold_text else ""
    css_style = f"""
    <style>
        [data-testid="stAppViewBlockContainer"] {{
            background-color: {background_color};
            line-height: {line_height};
            font-size: {font_size}px;
            {bold_style}
            color:{text_color} /* 添加字体颜色 */
        }}
        [data-testid="stAppViewBlockContainer"] p {{
            font-size: {font_size}px;
            {bold_style}
        }}
        
        #return-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #007BFF; /* 可以自定义颜色 */
            color: white;
            padding: 10px 10px;
            border-radius: 10px;
            text-decoration: none;
            cursor: pointer;
            font-size: 15px;
        }}
        
        #return-to-top:hover {{
            background-color: #0056b3; /* 鼠标悬停时的颜色 */
        }}
    </style>
    """

    # 定义返回顶部按钮
    return_to_top_tag = '<a href="#6ecb2d30" id="return-to-top">返回顶部</a>'

    if side.button("选取html文件"):
        result = threadpool()
        if result:
            st.session_state.result = result
        else:
            st.write("请选择HTML文件。")
            st.stop()
    return css_style, return_to_top_tag


st.set_page_config(page_title="HTML阅读器", page_icon=":book:", layout="wide")
style()
st.markdown('### HTML阅读器')
css_style, return_to_top_tag = sidebar_setting()

# 主体内容
# 如果用户选择了文件，则读取并显示文件内容
if "result" not in st.session_state:
    st.write("请选择HTML文件")

else:
    with st.sidebar:
        file_name_select, parent_dir = show_file_names(st.session_state.result)

    with open(parent_dir +"/"+ file_name_select, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    # 渲染HTML内容，并应用用户选择的样式
    st.html( css_style + file_content + return_to_top_tag)