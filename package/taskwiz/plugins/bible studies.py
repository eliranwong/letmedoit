"""
My Hand Bot Plugin - bible studies

add input suggestions and predefined instructions for bible studies

"""

from taskwiz import config

config.inputSuggestions.append("""Bible Topic.
Write about the following topic in reference to the Bible.
In addition, explain the significance of the topic in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.
[NO_FUNCTION_CALL]
Bible topic: """)
config.inputSuggestions.append("""Bible Place.
I will provide you with a location name.
Give me comprehensive information on this location in the bible.
If this singular name is used to denote various different locations in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this location in the bible.
[NO_FUNCTION_CALL]
Bible location: """)
config.inputSuggestions.append("""Bible Person.
I will provide you with a person name.
Give me comprehensive information on this person in the bible.
If this singular name is used to denote various different characters in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this person in the bible.
[NO_FUNCTION_CALL]
Bible preson name: """)

# Translation
config.inputSuggestions.append("""Bible Hebrew Verse Translation.
I would like to request your assistance as a bible translator.
I will provide you with a Hebrew bible verse text.
First, give me transliteration of the text.
Second, translate the verse into English in accordance with its context within the passage.
Remember, translate from the Hebrew text that I give you, do not copy an existing translation, as I want a completely new translation.
Third, map each Hebrew word with corresponding translation.
In mapping section, do include transliteration of each Hebrew word, so that each mapping are formatted in pattern this pattern: word | transliteration | corresponding translation.
Use "Transliteration:", "Translation:" and "Mapping:" as the section titles.
Remember, do not give parsing information, explanation or repeat the bible reference that I give you.
[NO_FUNCTION_CALL]
I am giving you the Hebrew verse text below: """)
config.inputSuggestions.append("""Bible Greek Verse Translation.
I would like to request your assistance as a bible translator.
I will provide you with a Greek bible verse text.
First, give me transliteration of the text.
Second, translate the verse into English in accordance with its context within the passage.
Remember, translate from the Greek text that I give you, do not copy an existing translation, as I want a completely new translation.
Third, map each Greek word with corresponding translation.
In mapping section, do include transliteration of each Greek word, so that each mapping are formatted in pattern this pattern: word | transliteration | corresponding translation.
Use "Transliteration:", "Translation:" and "Mapping:" as the section titles.
Remember, do not give parsing information, explanation or repeat the bible reference that I give you.
[NO_FUNCTION_CALL]
I am giving you the Greek verse text below: """)

# Book Features
config.inputSuggestions.append("""Bible Book Introduction.
Write a detailed introduction on a book in the bible, considering all the following questions:
1. Who is the author or attributed author of the book?
2. What is the date or time period when the book was written?
3. What is the main theme or purpose of the book?
4. What are the significant historical events or context surrounding the book?
5. Are there any key characters or figures in the book?
6. What are some well-known or significant passages from the book?
7. How does the book fit into the overall structure and narrative of the Bible?
8. What lessons or messages can be learned from the book?
9. What is the literary form or genre of the book (e.g. historical, prophetic, poetic, epistle, etc.)?
10. Are there any unique features or controversies surrounding the book?
I want the introduction to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the introduction, pertaining to the following bible book.
[NO_FUNCTION_CALL]
Bible book name:""")
config.inputSuggestions.append("""Bible Outline.
I am currently studying the following bible book and chapters and would appreciate it if you could provide me with a detailed outline for it.
I want an outline for all chapters of the bible book and chapters I am giving you.
Please divide it into several main sections and under each section, divide it into different passages.
Break down the passages into the smallest ones possible, as I am looking for a highly detailed outline.
Additionally, kindly provide a title for each passage.
Remember, use your own analysis based on the bible text instead of copying a published outline.
If chapters are not specified, provide an outline to cover all chapters of the bible book given.
[NO_FUNCTION_CALL]
Bible reference: """)

# Chapter Features
config.inputSuggestions.append("""Bible Chapter Summary.
Write a detailed interpretation on a bible chapter, considering all the following questions:
1. What is the overview of the chapter?
2. How are the verses in this chapter structured or organized?
3. Are there any key verses or passages in the chapter?
4. Are there any significant characters, events, or symbols in the chapter?
5. What is the main themes or messages of the chapter?
6. What historical or cultural context is important to understand the chapter?
7. How have theologians, scholars, or religious leaders interpreted this chapter?
8. Are there any popular interpretations or controversies related to this chapter?
9. How does this chapter relate to other chapters, books, or themes in the Bible?
10. What lessons or morals can be taken from the chapter?
I want your interpretation to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the interpretation, pertaining to the following bible chapter.
[NO_FUNCTION_CALL]
Bible chapter: """)

# Verse Features
config.inputSuggestions.append("""Bible OT Verse Interpretation.
Interpret the following verse in the light of its context, together with insights of biblical Hebrew studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content.
[NO_FUNCTION_CALL]
Bible verse: """)
config.inputSuggestions.append("""Bible NT Verse Interpretation.
Interpret the following verse in the light of its context, together with insights of biblical Greek studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content.
[NO_FUNCTION_CALL]
Bible verse: """)

# Studies
config.inputSuggestions.append("""Bible Perspective.
Tell me how we should understand the content, according to biblical perspectives and principles:
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Meaning.
Explain the meaning of the content in reference to the Bible:
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Summary.
Write a summary on the content in reference to the Bible:
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Sermon.
Write a sermon on the content in reference to the Bible:
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Prayer.
Write a prayer on the content in reference to the Bible:
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Short Prayer.
Write a short prayer on the content in reference to the Bible:
(Keep the prayer short and do not make it longer than a paragraph.)
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Key Words.
Identify key words in the content.
Elaborate on their importance in comprehending the context and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Key Themes.
Identify key themes or key messages in the content.
Elaborate on their importance in comprehending the content and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Theology.
Please write the theological messages conveyed in the content, in reference to the Bible.
In addition, explain the significance of the theological messages in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Promises.
Quote relevant Bible promises in relation to the content.
Explain how these promises are meant to provide comfort, hope, and guidance in my life.
[NO_FUNCTION_CALL]
""")
config.inputSuggestions.append("""Bible Passages.
Quote relevant Bible passages in relation to the content. Explain how these passages are related to the given content.
[NO_FUNCTION_CALL]
""")

# Instructions accoring to the given content
config.predefinedInstructions["Bible - Put in Perspective"] = """Tell me how we should understand it or response, according to biblical perspectives and principles. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Explain its Meaning"] = """Explain the meaning of the given content in reference to the Bible. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Write a Summary"] = """Write a summary in reference to the Bible. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Write a Sermon"] = """Write a sermon in reference to the Bible. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Write a Prayer"] = """Write a prayer in reference to the Bible. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Write a Short Prayer"] = """Write a short prayer in reference to the Bible.
Keep the prayer short and do not make it longer than a paragraph. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Explain Key Words"] = """Identify key words in the content.
Elaborate on their importance in comprehending the context and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Explain Key Themes"] = """Identify key themes or key messages in the content.
Elaborate on their importance in comprehending the content and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Explain Theology"] = """Please write the theological messages conveyed in the content, in reference to the Bible.
In addition, explain the significance of the theological messages in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Quote Promises"] = """Quote relevant Bible promises in relation to the content. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Quote Promises & Explain"] = """Quote relevant Bible promises in relation to the content. Explain how these promises are meant to provide comfort, hope, and guidance in my life. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Quote Passages"] = """Quote relevant Bible passages in relation to the content. [NO_FUNCTION_CALL]"""
config.predefinedInstructions["Bible - Quote Passages & Explain"] = """Quote relevant Bible passages in relation to the content. Explain how these passages are related to the given content. [NO_FUNCTION_CALL]"""
