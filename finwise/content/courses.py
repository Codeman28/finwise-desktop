"""
courses.py - The text of every course, lesson and quiz (in Vietnamese).

This file is pure DATA: no logic, no screens.  To add a lesson you only
add a new dictionary here - the Learn screen draws it automatically.

Lesson structure:
    id          unique text id (used to remember which lessons are done)
    title       shown in the lesson list
    minutes     rough reading time
    blocks      list of (type, text) pairs. Types:
                    "text"    - a normal paragraph
                    "tip"     - a highlighted tip box
                    "example" - a worked example box
                    "list"    - text lines separated by \n, shown as bullets
    quiz        list of questions: question, options, answer (index), why
    challenge   (optional) id of a matching playground challenge
"""

COURSES = [
    # ======================================================================
    {
        "id": "basics",
        "title": "Tài chính cơ bản",
        "subtitle": "Tiền của bạn đi đâu, và làm sao để làm chủ nó.",
        "color": "green",
        "lessons": [
            {
                "id": "basics-budget",
                "title": "Ngân sách là gì?",
                "minutes": 4,
                "challenge": "first-budget",
                "blocks": [
                    ("text", "Ngân sách đơn giản là một kế hoạch cho tiền của bạn. Trước khi "
                             "tháng mới bắt đầu, bạn quyết định sẽ chi bao nhiêu cho từng phần "
                             "của cuộc sống - tiền nhà, ăn uống, đi lại, giải trí - sao cho "
                             "tổng chi tiêu luôn thấp hơn số tiền bạn kiếm được."),
                    ("text", "Nếu không có kế hoạch, tiền thường 'bốc hơi' qua những khoản nhỏ. "
                             "Lập ngân sách không có nghĩa là bạn không được vui chơi; nó có "
                             "nghĩa là bạn chọn trước nơi tiền sẽ đi, thay vì cuối tháng mới "
                             "tự hỏi tiền đã đi đâu."),
                    ("list", "Ghi lại thu nhập hằng tháng (sau thuế).\n"
                             "Liệt kê các chi phí cố định: tiền nhà, hóa đơn, các gói đăng ký.\n"
                             "Đặt hạn mức cho các danh mục còn lại: thực phẩm, đi lại, giải trí.\n"
                             "Đảm bảo tổng các hạn mức nhỏ hơn thu nhập của bạn."),
                    ("example", "Mai kiếm được 15.000.000 ₫ mỗi tháng. Tiền nhà là 5.000.000 ₫. "
                                "Cô đặt hạn mức 3.000.000 ₫ cho thực phẩm, 800.000 ₫ cho đi lại "
                                "và 1.200.000 ₫ cho giải trí. Tổng kế hoạch: 10.000.000 ₫. "
                                "Còn lại 5.000.000 ₫ để tiết kiệm hoặc làm khoản dự phòng."),
                    ("tip", "Cứ bắt đầu đơn giản. Một ngân sách bạn thật sự dùng tốt hơn một "
                            "ngân sách hoàn hảo mà bạn bỏ cuộc sau một tuần. Hãy điều chỉnh mỗi tháng."),
                ],
                "quiz": [
                    {"question": "Mục đích chính của ngân sách là gì?",
                     "options": ["Để bạn không bao giờ tiêu tiền",
                                 "Để lên kế hoạch tiền sẽ đi đâu trước khi tiêu",
                                 "Để tính thuế thu nhập"],
                     "answer": 1,
                     "why": "Ngân sách là kế hoạch chi tiêu. Nó là về lựa chọn, không phải cấm đoán."},
                    {"question": "Thu nhập của bạn là 12.000.000 ₫. Tổng hạn mức các danh mục là "
                                 "14.000.000 ₫. Điều gì không ổn?",
                     "options": ["Không sao cả",
                                 "Bạn đang dự định chi nhiều hơn số tiền kiếm được",
                                 "Các hạn mức quá thấp"],
                     "answer": 1,
                     "why": "Chi tiêu dự kiến phải luôn thấp hơn thu nhập, nếu không bạn sẽ "
                            "thiếu tiền hoặc phải đi vay."},
                    {"question": "Bạn nên xem lại ngân sách bao lâu một lần?",
                     "options": ["Không bao giờ - đặt một lần là xong", "Khoảng mỗi tháng một lần",
                                 "Chỉ khi đang mắc nợ"],
                     "answer": 1,
                     "why": "Cuộc sống luôn thay đổi. Kiểm tra nhanh mỗi tháng giúp kế hoạch sát thực tế."},
                ],
            },
            {
                "id": "basics-needs-wants",
                "title": "Cần và muốn",
                "minutes": 3,
                "challenge": "needs-wants",
                "blocks": [
                    ("text", "Khoản CẦN là thứ bạn bắt buộc phải trả để sống và làm việc: chỗ ở, "
                             "thức ăn cơ bản, đi học hoặc đi làm, sức khỏe. Khoản MUỐN là thứ "
                             "làm cuộc sống dễ chịu hơn nhưng không có vẫn sống được: ăn nhà hàng, "
                             "quần áo mới chưa thật cần, các dịch vụ xem phim trực tuyến."),
                    ("text", "Một thứ có thể vừa cần vừa muốn. Đi chợ là khoản cần; đồ ăn vặt "
                             "đắt tiền trong hóa đơn đi chợ là khoản muốn. Hãy tự hỏi 'nếu không "
                             "mua thứ này thì điều gì sẽ xảy ra?' - đó là một phép thử nhanh."),
                    ("tip", "Khi eo hẹp, hãy cắt khoản muốn trước - đừng bao giờ bỏ khoản cần "
                            "như tiền nhà hay hóa đơn, vì phí trả chậm sẽ khiến mọi thứ tệ hơn."),
                    ("example", "Cần: tiền nhà 5.000.000 ₫, thực phẩm 2.500.000 ₫, xăng xe 300.000 ₫.\n"
                                "Muốn: ăn ngoài 1.200.000 ₫, trò chơi mới 600.000 ₫, vé ca nhạc 800.000 ₫."),
                ],
                "quiz": [
                    {"question": "Khoản nào sau đây thường là khoản CẦN?",
                     "options": ["Ốp lưng điện thoại mới", "Hóa đơn tiền điện", "Vé xem phim"],
                     "answer": 1,
                     "why": "Điện là thiết yếu cho cuộc sống hằng ngày; các khoản còn lại chỉ là có thì tốt."},
                    {"question": "Tháng này bạn bị thiếu tiền. Nên cắt khoản nào trước?",
                     "options": ["Tiền nhà", "Các khoản muốn như ăn ngoài", "Tiền xăng để đi làm"],
                     "answer": 1,
                     "why": "Hãy cắt khoản muốn trước. Bỏ khoản cần thường khiến bạn tốn kém hơn về sau."},
                    {"question": "Một phép thử nhanh cho khoản 'muốn' là...",
                     "options": ["Nó có đắt không?",
                                 "Không có nó, mình vẫn sống và làm việc bình thường chứ?",
                                 "Bạn bè mình có nó chưa?"],
                     "answer": 1,
                     "why": "Nếu cuộc sống và công việc vẫn ổn khi không có nó, đó là khoản muốn."},
                ],
            },
            {
                "id": "basics-tracking",
                "title": "Theo dõi chi tiêu",
                "minutes": 3,
                "challenge": "track-first-week",
                "blocks": [
                    ("text", "Theo dõi chi tiêu là ghi lại mỗi lần tiền vào hoặc tiền ra. Nghe "
                             "có vẻ nhàm chán, nhưng đây là thói quen giúp bạn hiểu về tiền "
                             "của mình nhiều nhất."),
                    ("text", "Hãy gắn danh mục cho mỗi khoản chi. Sau vài tuần bạn sẽ thấy quy luật: "
                             "có thể trà sữa tốn của bạn 1.000.000 ₫ mỗi tháng, hoặc tiền đi lại "
                             "rẻ hơn bạn nghĩ nhiều."),
                    ("list", "Ghi lại khoản chi ngay trong ngày - chỉ mất 10 giây.\n"
                             "Luôn dùng cùng một bộ danh mục.\n"
                             "Xem lại tổng chi mỗi tuần một lần."),
                    ("tip", "Trong FinWise, trang Giao dịch chính là sổ theo dõi, còn trang "
                            "Tổng quan tự động cho bạn thấy các quy luật."),
                ],
                "quiz": [
                    {"question": "Vì sao ta gắn danh mục cho mỗi khoản chi?",
                     "options": ["Để danh sách dài hơn",
                                 "Để thấy được quy luật tiền đi đâu",
                                 "Vì ngân hàng yêu cầu"],
                     "answer": 1,
                     "why": "Danh mục biến một danh sách dài thành những con số tổng hữu ích."},
                    {"question": "Khi nào là lúc tốt nhất để ghi lại một khoản chi?",
                     "options": ["Ngay trong ngày", "Cuối năm", "Chỉ khi mua đồ đắt tiền"],
                     "answer": 0,
                     "why": "Khoản chi nhỏ rất dễ quên - hãy ghi lại ngay."},
                    {"question": "Số dư của bạn bằng thu nhập trừ đi...",
                     "options": ["Các mục tiêu tiết kiệm", "Các khoản chi", "Các hạn mức ngân sách"],
                     "answer": 1,
                     "why": "Số dư = tiền vào - tiền ra."},
                ],
            },
        ],
    },
    # ======================================================================
    {
        "id": "budgeting",
        "title": "Lập ngân sách thông minh",
        "subtitle": "Những quy tắc đơn giản giúp bạn an toàn trước bất ngờ và nợ nần.",
        "color": "coral",
        "lessons": [
            {
                "id": "budget-503020",
                "title": "Quy tắc 50/30/20",
                "minutes": 4,
                "challenge": "rule-503020",
                "blocks": [
                    ("text", "Quy tắc 50/30/20 là điểm khởi đầu dễ dàng để chia thu nhập:"),
                    ("list", "50% cho khoản CẦN - nhà ở, thực phẩm, đi lại, hóa đơn.\n"
                             "30% cho khoản MUỐN - ăn ngoài, sở thích, mua sắm.\n"
                             "20% cho TIẾT KIỆM - quỹ khẩn cấp, mục tiêu, trả nợ."),
                    ("example", "Thu nhập 20.000.000 ₫ mỗi tháng:\n"
                                "Cần tối đa 10.000.000 ₫ · Muốn tối đa 6.000.000 ₫ · "
                                "Tiết kiệm ít nhất 4.000.000 ₫."),
                    ("text", "Đây là hướng dẫn, không phải luật. Nếu tiền nhà ở nơi bạn sống đắt "
                             "đỏ, khoản cần có thể lên tới 60% - khi đó hãy bớt khoản muốn để "
                             "tháng nào bạn cũng vẫn để dành được một ít."),
                    ("tip", "Trả cho mình trước: ngay khi nhận lương, hãy chuyển 20% vào tiết "
                            "kiệm trước khi bắt đầu tiêu, để việc tiết kiệm chắc chắn xảy ra."),
                ],
                "quiz": [
                    {"question": "Với thu nhập 15.000.000 ₫, theo 50/30/20 nên tiết kiệm bao nhiêu?",
                     "options": ["1.500.000 ₫", "3.000.000 ₫", "7.500.000 ₫"],
                     "answer": 1,
                     "why": "20% của 15.000.000 ₫ là 3.000.000 ₫."},
                    {"question": "'Ăn ngoài' thuộc phần nào trong 50/30/20?",
                     "options": ["50% khoản cần", "30% khoản muốn", "20% tiết kiệm"],
                     "answer": 1,
                     "why": "Ăn nhà hàng là một khoản muốn."},
                    {"question": "'Trả cho mình trước' nghĩa là gì?",
                     "options": ["Mua món gì đó thật xịn ngày nhận lương",
                                 "Để dành phần tiết kiệm ngay khi nhận lương",
                                 "Trả tiền nhà trễ"],
                     "answer": 1,
                     "why": "Tiết kiệm trước nghĩa là không phó mặc cho số tiền còn lại cuối tháng."},
                ],
            },
            {
                "id": "budget-emergency",
                "title": "Quỹ khẩn cấp",
                "minutes": 3,
                "challenge": "emergency-fund",
                "blocks": [
                    ("text", "Quỹ khẩn cấp là khoản tiền để riêng CHỈ dành cho những bất ngờ thật "
                             "sự: điện thoại cần cho công việc bị hỏng, hóa đơn viện phí, mất việc."),
                    ("text", "Không có quỹ này, bất ngờ thường được trả bằng thẻ tín dụng - và "
                             "tiền lãi khiến nó ngày càng đắt hơn mỗi tháng."),
                    ("list", "Mục tiêu đầu tiên: một quỹ nhỏ, ví dụ 5.000.000-10.000.000 ₫.\n"
                             "Mục tiêu dài hạn: 3 đến 6 tháng chi phí thiết yếu.\n"
                             "Giữ ở nơi an toàn và dễ rút, như tài khoản tiết kiệm."),
                    ("example", "Chi phí thiết yếu của bạn là 10.000.000 ₫ mỗi tháng. Quỹ 3 tháng "
                                "là 30.000.000 ₫. Để dành 2.000.000 ₫ mỗi tháng thì sau 15 tháng "
                                "bạn sẽ đạt được."),
                    ("tip", "Đợt giảm giá không phải là trường hợp khẩn cấp! Hãy đặt ra quy tắc "
                            "dùng quỹ trước khi bạn cần đến nó."),
                ],
                "quiz": [
                    {"question": "Đâu là một trường hợp khẩn cấp thật sự?",
                     "options": ["Đợt giảm giá 50%", "Xe máy bị hỏng mà bạn cần nó để đi làm",
                                 "Vé ca nhạc vừa mở bán"],
                     "answer": 1,
                     "why": "Khẩn cấp là việc bất ngờ VÀ cần thiết."},
                    {"question": "Mục tiêu dài hạn phổ biến cho quỹ khẩn cấp là...",
                     "options": ["1 tuần chi tiêu", "3 đến 6 tháng chi phí thiết yếu",
                                 "10 năm thu nhập"],
                     "answer": 1,
                     "why": "3-6 tháng đủ để vượt qua hầu hết các trường hợp mất việc hay sửa chữa lớn."},
                    {"question": "Vì sao quỹ khẩn cấp tốt hơn thẻ tín dụng khi gặp bất ngờ?",
                     "options": ["Thẻ tín dụng tính lãi",
                                 "Thẻ tín dụng là bất hợp pháp", "Không có gì khác nhau"],
                     "answer": 0,
                     "why": "Đi vay thì mất tiền lãi; dùng tiền tiết kiệm của mình thì không."},
                ],
            },
            {
                "id": "budget-debt",
                "title": "Tránh bẫy nợ",
                "minutes": 4,
                "challenge": "debt-lab",
                "blocks": [
                    ("text", "Nợ là dùng tiền bây giờ và trả lại sau - kèm theo TIỀN LÃI, tức "
                             "cái giá của việc đi vay. Thẻ tín dụng thường tính lãi 20-36% mỗi năm."),
                    ("text", "Cái bẫy: chỉ trả số tiền tối thiểu. Phần lớn khoản trả nhỏ đó dùng "
                             "để trả lãi, nên nợ gần như không giảm và có thể kéo dài nhiều năm."),
                    ("example", "Nợ thẻ 50.000.000 ₫ với lãi 24%/năm tốn khoảng 1.000.000 ₫ tiền lãi "
                                "ngay tháng đầu. Trả 1.200.000 ₫ thì chỉ khoảng 200.000 ₫ dùng để giảm "
                                "nợ. Trả 5.000.000 ₫ thì khoảng một năm là hết nợ."),
                    ("list", "Trả nhiều hơn mức tối thiểu bất cứ khi nào có thể.\n"
                             "Trả khoản nợ có lãi suất cao nhất trước.\n"
                             "Tránh 'mua trước trả sau' cho các khoản muốn."),
                    ("tip", "Thử Phòng lab Nợ ở mục Luyện tập để xem số tiền trả mỗi tháng "
                            "thay đổi tổng chi phí ra sao."),
                ],
                "quiz": [
                    {"question": "Tiền lãi là gì?",
                     "options": ["Tiền thưởng miễn phí từ ngân hàng", "Cái giá bạn trả khi đi vay tiền",
                                 "Một loại thuế"],
                     "answer": 1,
                     "why": "Tiền lãi là chi phí cho việc dùng tiền của người khác."},
                    {"question": "Vì sao chỉ trả mức tối thiểu lại rủi ro?",
                     "options": ["Không rủi ro gì cả",
                                 "Phần lớn dùng để trả lãi, nên nợ kéo dài lâu hơn nhiều",
                                 "Ngân hàng sẽ đóng tài khoản của bạn"],
                     "answer": 1,
                     "why": "Khoản trả nhỏ gần như không chạm tới số nợ gốc."},
                    {"question": "Bạn có hai khoản nợ. Nên trả khoản nào trước?",
                     "options": ["Khoản có lãi suất cao nhất",
                                 "Khoản có tấm thẻ đẹp nhất", "Khoản mới nhất"],
                     "answer": 0,
                     "why": "Lãi suất cao nhất khiến bạn tốn nhiều tiền nhất mỗi tháng."},
                ],
            },
        ],
    },
    # ======================================================================
    {
        "id": "growing",
        "title": "Làm tiền lớn lên",
        "subtitle": "Mục tiêu, lãi kép và lạm phát ảnh hưởng đến bạn thế nào.",
        "color": "pink",
        "lessons": [
            {
                "id": "grow-goals",
                "title": "Đặt mục tiêu tiết kiệm",
                "minutes": 3,
                "challenge": "goal-plan",
                "blocks": [
                    ("text", "Mục tiêu tiết kiệm biến câu 'mình nên tiết kiệm' thành điều cụ thể: "
                             "một cái tên, một số tiền và một thời hạn."),
                    ("list", "Cụ thể: 'Laptop cho năm nhất đại học', không phải 'mấy thứ linh tinh'.\n"
                             "Đo được: 24.000.000 ₫.\n"
                             "Có thời hạn: trong 12 tháng -> 2.000.000 ₫ mỗi tháng."),
                    ("text", "Lấy số tiền chia cho số tháng để biết mỗi tháng cần để dành bao nhiêu. "
                             "Nếu con số quá cao, hãy kéo dài thời gian hoặc giảm mục tiêu."),
                    ("tip", "Nhìn thấy tiến độ rất có động lực - trang Mục tiêu có thanh tiến độ "
                            "cho từng mục tiêu."),
                ],
                "quiz": [
                    {"question": "Bạn muốn có 6.000.000 ₫ trong 6 tháng. Mỗi tháng cần bao nhiêu?",
                     "options": ["600.000 ₫", "1.000.000 ₫", "6.000.000 ₫"],
                     "answer": 1,
                     "why": "6.000.000 ₫ / 6 tháng = 1.000.000 ₫ mỗi tháng."},
                    {"question": "Mục tiêu nào được viết tốt nhất?",
                     "options": ["Tiết kiệm nhiều hơn", "Để dành 9.000.000 ₫ mua điện thoại mới trước tháng 6",
                                 "Trở nên giàu có"],
                     "answer": 1,
                     "why": "Nó có số tiền, mục đích và thời hạn rõ ràng."},
                    {"question": "Số tiền mỗi tháng quá cao so với bạn. Bạn có thể làm gì?",
                     "options": ["Bỏ cuộc", "Kéo dài thời hạn hoặc giảm mục tiêu",
                                 "Đi vay tiền"],
                     "answer": 1,
                     "why": "Điều chỉnh kế hoạch cho phù hợp với ngân sách thực tế của bạn."},
                ],
            },
            {
                "id": "grow-compound",
                "title": "Phép màu của lãi kép",
                "minutes": 4,
                "challenge": "growth-lab",
                "blocks": [
                    ("text", "Khi gửi tiền vào tài khoản có lãi, bạn nhận lãi trên số tiền đã gửi. "
                             "Năm sau, bạn CÒN nhận lãi trên cả tiền lãi của năm trước. Hiệu ứng "
                             "'lăn cầu tuyết' đó gọi là lãi kép."),
                    ("example", "10.000.000 ₫ với lãi 5% mỗi năm:\n"
                                "Năm 1: 10.500.000 ₫ · Năm 2: 11.025.000 ₫ · Năm 10: khoảng 16.290.000 ₫.\n"
                                "Bạn không gửi thêm đồng nào - phần tăng thêm đến từ lãi của tiền lãi."),
                    ("text", "Hai yếu tố quan trọng nhất là THỜI GIAN và gửi ĐỀU ĐẶN. "
                             "Bắt đầu sớm quan trọng hơn bắt đầu với số tiền lớn."),
                    ("tip", "Mở Phòng lab Tăng trưởng ở mục Luyện tập và kéo các thanh trượt - "
                            "xem điều gì xảy ra khi bạn tăng gấp đôi số năm."),
                ],
                "quiz": [
                    {"question": "Lãi kép nghĩa là nhận lãi trên...",
                     "options": ["Chỉ khoản gửi đầu tiên", "Tiền gửi VÀ cả tiền lãi trước đó",
                                 "Tiền của người khác"],
                     "answer": 1,
                     "why": "Tiền lãi được cộng vào số dư, rồi chính nó cũng sinh lãi."},
                    {"question": "Điều gì thường giúp lãi kép hiệu quả nhất?",
                     "options": ["Bắt đầu sớm", "Kiểm tra số dư mỗi ngày",
                                 "Giữ tiền mặt ở nhà"],
                     "answer": 0,
                     "why": "Càng nhiều năm = càng nhiều vòng lãi chồng lãi."},
                    {"question": "10.000.000 ₫ với lãi 10%/năm trong 2 năm (tính lãi hằng năm) sẽ thành...",
                     "options": ["12.000.000 ₫", "12.100.000 ₫", "11.000.000 ₫"],
                     "answer": 1,
                     "why": "Năm 1: 11.000.000 ₫. Năm 2: 11.000.000 ₫ + 10% = 12.100.000 ₫."},
                ],
            },
            {
                "id": "grow-inflation",
                "title": "Lạm phát và đầu tư cơ bản",
                "minutes": 4,
                "challenge": None,
                "blocks": [
                    ("text", "Lạm phát là việc giá cả tăng dần theo thời gian. Nếu lạm phát là "
                             "3% mỗi năm, món đồ giá 100.000 ₫ hôm nay sẽ tốn khoảng 103.000 ₫ "
                             "vào năm sau. Tiền cất dưới gối sẽ mua được ít đi."),
                    ("text", "Đó là lý do mọi người gửi tiết kiệm có lãi, và một số người đầu tư "
                             "cho mục tiêu dài hạn. Đầu tư (ví dụ vào các quỹ nắm giữ nhiều công ty) "
                             "có thể tăng nhanh hơn gửi tiết kiệm, nhưng giá trị có thể lên VÀ xuống."),
                    ("list", "Có quỹ khẩn cấp trước - đừng đầu tư số tiền bạn có thể sớm cần đến.\n"
                             "Phân tán rủi ro: nhiều công ty, không phải một.\n"
                             "Nghĩ dài hạn: tính bằng năm, không phải bằng tuần.\n"
                             "Nếu ai đó hứa lợi nhuận cao mà không rủi ro, rất có thể đó là lừa đảo."),
                    ("tip", "Bài học này mang tính giáo dục chung, không phải lời khuyên tài chính. "
                            "Với các quyết định cá nhân, hãy hỏi ý kiến chuyên gia có chuyên môn."),
                ],
                "quiz": [
                    {"question": "Nếu lạm phát là 3%, 100.000 ₫ tiền đi chợ năm sau sẽ tốn khoảng...",
                     "options": ["97.000 ₫", "100.000 ₫", "103.000 ₫"],
                     "answer": 2,
                     "why": "Giá tăng khoảng 3%."},
                    {"question": "Điều gì nên có TRƯỚC khi đầu tư?",
                     "options": ["Quỹ khẩn cấp", "Mua một chiếc xe thể thao",
                                 "Không cần gì, đầu tư tất cả"],
                     "answer": 0,
                     "why": "Khoản đầu tư có thể giảm giá; bạn cần tiền an toàn cho những bất ngờ trước."},
                    {"question": "'Cam kết lãi 50% mỗi tháng, không rủi ro!' nhiều khả năng là...",
                     "options": ["Một cơ hội tuyệt vời", "Lừa đảo", "Chuyện bình thường của ngân hàng"],
                     "answer": 1,
                     "why": "Lợi nhuận cao luôn đi kèm rủi ro cao. 'Không rủi ro' + lãi khủng = dấu hiệu cảnh báo."},
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Small lookup helpers so screens do not have to loop through COURSES
# ---------------------------------------------------------------------------
def all_lessons():
    """Every lesson in order, as one flat list."""
    lessons = []
    for course in COURSES:
        lessons.extend(course["lessons"])
    return lessons


def find_lesson(lesson_id):
    """Return (course, lesson) for a lesson id, or (None, None) if unknown."""
    for course in COURSES:
        for lesson in course["lessons"]:
            if lesson["id"] == lesson_id:
                return course, lesson
    return None, None


def next_unfinished_lesson(completed_ids):
    """The first lesson the learner has not finished yet (or None if all done)."""
    for lesson in all_lessons():
        if lesson["id"] not in completed_ids:
            return lesson
    return None


# Short tips shown on the dashboard, one per day.
DAILY_TIPS = [
    "Trả cho mình trước: để dành tiền tiết kiệm ngay ngày nhận lương, trước khi tiêu.",
    "Chờ 24 giờ trước mọi khoản mua ngoài kế hoạch trên 500.000 ₫.",
    "Hủy một gói đăng ký bạn không dùng trong tháng này.",
    "Một quỹ khẩn cấp nhỏ 5.000.000 ₫ đã giúp tránh được nhiều khoản nợ.",
    "Xem lại ngân sách mỗi tháng một lần - chỉ mất 10 phút.",
    "Nấu ăn ở nhà thêm một bữa mỗi tuần; cộng dồn lại rất đáng kể.",
    "Luôn trả nhiều hơn mức tối thiểu của thẻ tín dụng.",
]
