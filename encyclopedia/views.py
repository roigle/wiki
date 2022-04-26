from django.shortcuts import render, redirect
from django import forms

from . import util

import markdown2
import random


""" Create a class for the form to create a new entry """
class NewForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title of the entry', 'class': 'form-control formwidth'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write your complete Markdown text here', 'class': 'form-control formwidth'}))



""" Generates the index page with a (clickable) list of all the entries """
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


"""
Entry Page: Visiting /wiki/TITLE, where TITLE is the title of an encyclopedia entry, should render a page that displays the contents of that encyclopedia entry.
- The view should get the content of the encyclopedia entry by calling the appropriate util function.
- If an entry is requested that does not exist, the user should be presented with an error page indicating that their requested page was not found.
- If the entry does exist, the user should be presented with a page that displays the content of the entry. The title of the page should include the name of the entry.
"""
def article(request, title):
    if util.get_entry(title):
        text = markdown2.markdown(util.get_entry(title))
    else:
        title = "Page Not Found"
        text = None

    return render(request, "encyclopedia/article.html", {
        "title": title,
        "text": text
    })


"""
Search: Allow the user to type a query into the search box in the sidebar to search for an encyclopedia entry.
- If the query does not match the name of an encyclopedia entry,
the user should instead be taken to a search results page that displays a list of all encyclopedia entries
that have the query as a substring.
For example, if the search query were ytho, then Python should appear in the search results.
- Clicking on any of the entry names on the search results page should take the user to that entry’s page.
"""
def search(request):
    # get the search term
    term = request.GET["q"]

    # handle the case that the user doesn't input anything
    if not term:
        return redirect(index)

    # get the list of entries
    entries = util.list_entries()

    # to be able see if the term is on the list regardless of case, we'll lower both the term and the entries
    termlow = term.lower()
    entrieslow = list(map(lambda x: x.lower(), entries))

    # now, we'll see if the term is on the entries BUT
    # if it is, we have to send it to the article func on the same case as the original entry
    for x in range(len(entrieslow)):
        if termlow == entrieslow[x]:
            return redirect(article, title=entries[x])
    
    # if the term is not on the entries (therefore the for loop would finish), handle it as per the instructions above
    # first, create a list to store the possible matches
    matches = []

    # go through the entries again and see if the term matches any parts of each entry
    # if it does, add the original entry to the matches
    for x in range(len(entrieslow)):
        if termlow in entrieslow[x]:
            matches.append(entries[x])

    # finally, generate the html with the possible matches
    return render(request, "encyclopedia/search.html", {
        "matches": matches,
        "term": term
    })
    

"""
Random Page: Clicking “Random Page” in the sidebar should take user to a random encyclopedia entry.
"""
def randompage(request):
    # first, create a list with the entries:
    entries = util.list_entries()

    # get a random number within the list
    # that is, the number will be a position in the list
    # ex: if the index is 2, we will use it later to select entries[2]
    index = int(random.random() * len(entries))

    # redirect to the func article, passing the selected entry as the title
    return redirect(article, title=entries[index])


"""
New Page: Clicking “Create New Page” in the sidebar should take the user to a page where they can create a new encyclopedia entry.
- Users should be able to enter a title for the page and, in a textarea, should be able to enter the Markdown content for the page.
- Users should be able to click a button to save their new page.
- When the page is saved, if an encyclopedia entry already exists with the provided title, the user should be presented with an error message.
- Otherwise, the encyclopedia entry should be saved to disk, and the user should be taken to the new entry’s page.
"""
def newpage(request):
    # if the user got here by POST (that is, submitting the form), handle it
    if request.method == "POST":
                
        # get the info of the form
        form = NewForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]

            # check if the entry already exists: compare the title against the entries (see search for lower etc)
            # get the list of entries
            entries = util.list_entries()

            # to be able see if the term is on the list regardless of case, we'll lower both the term and the entries
            titlelow = title.lower()
            entrieslow = list(map(lambda x: x.lower(), entries))

            # now, we'll see if the term is on the entries
            for x in range(len(entrieslow)):
                # if it exists, send the user to a "already exists" page (give them the option to edit it)
                if titlelow == entrieslow[x]:
                    return render(request, "encyclopedia/newpage.html", {
                        "form": form,
                        "entry": entries[x]
                    })

            # if it doesn't exist (therefore exiting the for loop), save it (call util.save_entry)
            # and then redirect the user to that entry page
            util.save_entry(title, text)
            return redirect(article, title=title)
        
        # if the form is NOT valid, return the user to the newpage with the form filled in:
        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": form
            })

    # else, if the user got here by GET, present the form for them to fill in
    else:
        return render(request, "encyclopedia/newpage.html", {
            "form": NewForm()
        })


"""
Edit Page: On each entry page, the user should be able to click a link to be taken to a page where the user can edit that entry’s Markdown content in a textarea.
- The textarea should be pre-populated with the existing Markdown content of the page. (i.e., the existing content should be the initial value of the textarea).
- The user should be able to click a button to save the changes made to the entry.
- Once the entry is saved, the user should be redirected back to that entry’s page.
"""
def editpage(request, title):
    
    # if the user got here when submitting the edit form, handle it
    if request.method == "POST":
        
        # get the info of the form
        form = NewForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]

            # save the entry
            util.save_entry(title, text)

            # redirect the user to the entry they've just edited
            return redirect(article, title=title)
        
        # if the form is NOT valid, return the user to the newpage with the form filled in:
        else:
            return render(request, "encyclopedia/editpage.html", {
                "form": form
            })

    # else, if the user got here by GET (that is, clicking on the "edit" link), present the populated form for them to edit
    else:
        # get the title of the entry they're trying to edit
        title = request.GET.get(title, title)

        # get the content of the entry from the .md file
        text = util.get_entry(title)

        return render(request, "encyclopedia/editpage.html", {
            "title": title,
            "text": text
        })
