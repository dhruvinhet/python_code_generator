# -*- coding: utf-8 -*

"""
Main entry point for the blog generator.
This script takes a title as input and generates a blog post for it.
"""

import os
import sys
import random

# Dummy function for generating a blog post.  In a real application, this would use
# an LLM or some other sophisticated method to generate the content.
def generate_blog_post(title):
    """Generates a dummy blog post based on the given title."""
    paragraphs = []
    num_paragraphs = random.randint(3, 5)
    for _ in range(num_paragraphs):
        num_sentences = random.randint(5, 8)
        sentences = []
        for _ in range(num_sentences):
            sentences.append(f"This is a sentence about {title}.")
        paragraphs.append(" ".join(sentences))
    return "\n\n".join(paragraphs)


def main():
    """
    Main function to handle user input and generate the blog post.
    """
    try:
        title = input("Enter the title for the blog post: ")
        if not title:
            raise ValueError("Title cannot be empty.")
        
        blog_post = generate_blog_post(title)
        
        print("\nGenerated Blog Post:\n")
        print(blog_post)

        # Optionally, save the blog post to a file
        save_to_file = input("Do you want to save the blog post to a file? (y/n): ").lower()
        if save_to_file == 'y':
            filename = title.replace(" ", "_") + ".txt"
            with open(filename, "w") as f:
                f.write(blog_post)
            print(f"Blog post saved to {filename}")
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()