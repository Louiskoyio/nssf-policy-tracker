def inject_custom_styles():
    return """
    <style>
        /* === Global Reset === */
        * {
            box-sizing: border-box;
        }

        /* === Policy Card === */
        .policy-card {
            border: 2px solid #c1d72d;
            background-color: #ffffff;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        /* === Policy Table === */
        .policy-table {
            width: 100%;
            border-collapse: collapse;
        }

        .policy-table td {
            padding: 8px;
            border: none;
            vertical-align: top;
        }

        .policy-table tr {
            border-bottom: 1px solid #d7d7d7;
        }

        .policy-table .label {
            font-weight: bold;
            color: black;
            width: 180px;
        }

        /* === Input Fields === */
        input[type="text"],
        input[type="number"],
        input[type="email"],
        input[type="date"],
        select,
        textarea {
            background-color: white !important;
            border: 2px solid #c1d72d !important;
            color: black !important;
            font-weight: bold !important;
            padding: 8px !important;
            border-radius: 6px !important;
        }

        /* === Buttons === */
        .stButton > button {
            background-color: #1A8F2D !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease-in-out;
        }

        .stButton > button:hover {
            background-color: #c1d72d !important;
            color: black !important;
        }

        /* === Sidebar Menu Custom === */
        .custom-sidebar {
            margin-top: 1rem;
        }

        .custom-sidebar a {
            display: block;
            padding: 10px 15px;
            margin-bottom: 5px;
            color: black;
            text-decoration: none;
            font-weight: bold;
            border-radius: 6px;
            transition: background-color 0.3s ease-in-out;
        }

        .custom-sidebar a:hover {
            background-color: #c1d72d;
            color: black;
        }

        .custom-sidebar a.active {
            background-color: #1A8F2D;
            color: white;
        }
    </style>
    """
