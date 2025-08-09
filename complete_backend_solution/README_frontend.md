## Interacting with the API

* [API documentation](http://127.0.0.1:8000/docs)
    * this is for the local version, otherwise you'll find it at apiURL/docs
* example website html: complete_backend_solution/tests/component_matcher.html
    * run api.py in the src folder then open the html file in a browser

### General Idea

When using the api the general idea is that you have a product in mind that you want to find. In this case you use the
API's get methods in order to find the category of product you want. Then once you find that you will then build a
search request specified by the user as to what they are looking for in this product. Then after building out that
search request it is posted as a JSON to the API and returned scored results, see the backend documentation for more
details on how this process works. With the returned results will also be a session id which then can be used to request
formatting changes like sorting in a search/session_id request. All that is passed there is a session id and a retrieve
requested posted as a JSON.

honestly, i think the best resource for this will be an example so i'll write one here and then the website and 
documentation should be enough for technical details.

Also might put the flow chart of our idea of how the front end will work here just as a suggestion.


### Notes for consideration
- filter does NOTHING if non numeric column is passed to it (can be swapped for a valueError)
- scores are returns unrounded

