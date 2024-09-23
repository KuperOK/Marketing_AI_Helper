prompt_for_title = """You are an expert at creating detailed product titles for an online store.
I need three different long product titles for an item based on its technical specifications provided below.
The titles should be optimized for search engines, customer-friendly,
and include the most important technical details in a concise but informative way.
Here are the technical specifications for the product:\n{tech_info}

Example: Here's an example of a long product title for reference: {prod_long_name}

Please generate three product title variations for the given technical information using this format and structure.
Don't use any info from analog and don't use Device Name displayed in Network.
Show only your names without any comments.

Remember! Output text language must be {language}
"""


prompt_for_benefits = """You are an expert in marketing and product descriptions. 
I need you to create three customer-oriented benefits for an item based on its technical specifications provided below. 
The benefits should be simple, clear, and highlight how the product can improve the user's experience.

Here are the technical specifications for the product:
{tech_info}

Additionally, you may refer to the description of a similar product provided below to inspire the benefits:
{product_decription}

Here is an example for another item:
- "Promotes peaceful sleep with soothing light effects"
- "Easy to use – perfect atmosphere for children’s rooms"
- "Creative gift: transforms any room into a starry sky"

Please generate three benefit descriptions for the given product not longer 80 symbols, focusing on how it solves user problems or adds value. Show only your responses without any comments.

Remember! Output text language must be {language}
"""

prompt_for_USP = """
You are an expert in marketing and product descriptions. 
I need you to create six customer-oriented Unique Selling Points for an item based on its technical specifications provided below. 
The Unique Selling Points should be simple, clear, and highlight how the product can improve the user's experience.

Here are the technical specifications for the product:
{tech_info}

Additionally, you may refer to the description of a similar product provided below to inspire the  Unique Selling Points:
{product_decription}

Additionally, you may refer to the comments of a similar product provided below to inspire the  Unique Selling Points:
{product_comments}

Here is an example for another item:
*Version 1:
-Unique 3D Northern Lights: Create a magical atmosphere.
-18 lighting modes: The right lighting for every mood.
-Energy-saving: Low power consumption with DC5V.
-Easy to use: Easy to switch between different modes.
-Compact design: Fits perfectly in any child's room.
-Robust and safe: Made from durable materials.
*Version 2:
-Realistic star projection: Creates a magical environment.
-Various light settings: Adapts to every mood.
-Safe and durable: Suitable for everyday use.
-Easy installation: Ready to use quickly and very easy to use.
-Perfect as a gift: Ideal for children's birthdays and festive occasions.
-Silent operation: No annoying noises during use.
*Version 3:
-Creative light show: Delights children with changing colors.
-Environmentally friendly: Low energy consumption for longer use.
-Child-friendly design: Safe and easy to use.
-Long-lasting LED technology: Lasts longer and offers consistent quality.
-Mobile use: Can be used anywhere thanks to its compact format.
-Attractive design: Fits into any interior design in a child's room.

Please generate three different variants by six USP in eschbenefit descriptions for the given product, focusing on uniqueness, Customer Benefits and Competitive advantages.
Length of each USP no more than 85 characters
Show only your responses without any comments.

Remember! Output text language must be {language}
"""

prompt_for_ad_text = """
Create an advertising text of up to 3000 characters for a product with the following technical specifications: 
{tech_info}.
You may use as example of advertising text the description of a similar product provided below: 
{product_decription}.
Strictly prohibited use technical info from product description for advertising texts

Additionally, you can utilize in general useful insights from customer reviews, but do not directly reference them in the text.
Сustomer reviews:
{product_comments}

Strictly prohibited use technical info from customer review for advertising texts

Begin with a short, general introduction (maximum 2-3 sentences). 
Then, write between 3 to 6 meaningful paragraphs, each starting with **6 promotional words** that describe the feature highlighted in that paragraph. 
These 6 words should be bolded, followed by the rest of the text after a colon.

List the technical aspects of the product in a bullet-point format, using as many points as needed. 
Please emphasize the most important information by making it bold. Befor technical info paste `Technical details: ` 

Please create 3 variations:
1. Highly technical description
2. Less technical description
3. More conversational, user-friendly tone

Take into account - In advertising text you can add only info from technical specifications and dont use it from similar product. It is very importantly/
Strictly prohibited using technical info of similar product for advertising texts only from {tech_info} 
Show only your responses without any comments.

Remember! Output text language must be {language}
"""

prompt_for_translate = """
You experienced translator and ploglit. \
Please translate the following marketing text from {source_language} to {target_language}.\
Pay attention to style, context, and specific expressions. Save all formatting as in original text.\
Text for translation:\n\
{text_for_translation}
"""