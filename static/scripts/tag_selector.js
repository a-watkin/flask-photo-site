"use strict";

const e = React.createElement;

class TagSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      original: null,
      title: null,
      tags: null,
      selectedTags: [],
      albumId: null
    };

    this.tagClick = this.tagClick.bind(this);
  }

  componentWillMount() {
    // console.log("hello from componentWillMount");
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("=");
    let albumId = splitUrl[1];

    fetch(`/api/get/phototags?photo_id=${albumId}`)
      .then(res => res.json())
      .then(
        result => {
          // ok i am getting the data
          // console.log(`result ${result}`, Object.keys(result), result.original);
          this.setState({
            isLoaded: true,
            original: result.original,
            title: result.title,
            tags: result.tags,
            selectedTags: [],
            albumId: albumId
          });
        },
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  tagClick(tagName) {
    console.log("clicked", tagName);
    let tempTags = [...this.state.selectedTags];
    console.log(tempTags);
    if (tempTags.indexOf(tagName) === -1) {
      tempTags.push(tagName);
    } else {
      console.log("getting here on first try?");
      tempTags.splice(tempTags.indexOf(tagName), 1);
    }
    console.log(
      "should be altering state here",
      tempTags,
      this.state.selectedTags
    );

    this.setState({
      selectedTags: tempTags
    });
    // so for some reason it's just not updated yet
    // when you try and get the state here?
    console.log("what", this.state.selectedTags);
  }

  render() {
    let cardStyle = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px"
    };

    let selectedTag = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px",
      backgroundColor: "#28a745",
      color: "white"
    };

    console.log("what is it here?", this.state.selectedTags);

    if (this.state.isLoaded) {
      const tagData = this.state.tags;

      const tag = tagData.map((tag, index) => {
        console.log(tag, index);
        const tagName = tag["tag_name"];
        return (
          <div key={index}>
            <button
              type="button"
              className="btn btn-outline-success btn-lg"
              onClick={() => this.tagClick(tagName)}
            >
              {tagName}
            </button>
          </div>
        );
      });

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <img className="img-fluid" src={this.state.original} alt="" />
            </div>

            <div className="col">
              <h3>
                {" "}
                Tags for the photo{" "}
                <span className="font-weight-bold font-italic">
                  {" "}
                  {this.state.title}{" "}
                </span>
              </h3>
              <p>Select tags to remove by clicking on them below.</p>
              <hr />
              {tag}
            </div>
          </div>
          <hr />
          <div className="row">
            <div className="col text-center">
              <button className="btn btn-success btn-lg">
                Return to photo
              </button>
            </div>

            <div className="col text-center">
              <button className="btn btn-danger btn-lg"> Remove tags </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div>
        <div className="row">
          <div className="col text-center">
            <h2>Problem getting data.</h2>
          </div>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#tag-selector");
ReactDOM.render(e(TagSelector), domContainer);
