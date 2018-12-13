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
      photoId: null
    };

    this.tagClick = this.tagClick.bind(this);
  }

  componentWillMount() {
    // console.log("hello from componentWillMount");
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("=");
    let photoId = splitUrl[1];

    fetch(`/api/get/phototags?photo_id=${photoId}`)
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
            photoId: photoId
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

  backToPhoto() {
    window.location.assign(`/api/photos/${this.state.albumId}`);
  }

  sendData() {
    console.log("clicked on remove tag");
    if (this.state.selectedTags.length < 1) {
      console.log("do nothing if no tag has been selected");
      return false;
    }

    console.log("getting here?", this.state.selectedAlbum);
    fetch("/api/get/phototags", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: this.state.photoId,
        selectedTags: this.state.selectedTags
      })
    }).then(() => {
      console.log("sent data");
      // redirect after successful post
      // window.location.assign(
      //   `http://127.0.0.1:5000/albums/${this.state.selectedAlbum[0]}`
      // );
    });
  }

  render() {
    let notSelected = {
      // width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px"
    };

    let selectedTag = {
      // width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px",
      backgroundColor: "#dc3545",
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
              className={
                this.state.selectedTags.includes(tagName)
                  ? "btn btn-outline-danger btn-lg"
                  : "btn btn-outline-success btn-lg"
              }
              onClick={() => this.tagClick(tagName)}
              style={
                this.state.selectedTags.includes(tagName)
                  ? selectedTag
                  : notSelected
              }
            >
              {tagName}
            </button>
          </div>
        );
      });

      return (
        <div>
          <div className="row text-center">
            <div className="col my-auto">
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
              <button
                className="btn btn-success btn-lg"
                onClick={() => this.backToPhoto()}
              >
                Return to photo
              </button>
            </div>

            <div className="col text-center">
              <button
                className="btn btn-danger btn-lg"
                onClick={() => this.sendData()}
              >
                {" "}
                Remove tags{" "}
              </button>
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
