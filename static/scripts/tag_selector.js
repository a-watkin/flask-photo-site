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
    // Getting the album id from the URL.
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("=");
    let photoId = splitUrl[1];

    fetch(`/photo/tag/api/get/phototags?photo_id=${photoId}`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(
        result => {
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
    let tempTags = [...this.state.selectedTags];
    if (tempTags.indexOf(tagName) === -1) {
      tempTags.push(tagName);
    } else {
      tempTags.splice(tempTags.indexOf(tagName), 1);
    }
    this.setState({
      selectedTags: tempTags
    });
  }

  backToPhoto() {
    window.location.assign(`/photo/${this.state.photoId}`);
  }

  sendData() {
    if (this.state.selectedTags.length < 1) {
      return false;
    }
    fetch("/photo/tag/api/get/phototags", {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: this.state.photoId,
        selectedTags: this.state.selectedTags
      })
    }).then(() => {
      // Redirect after successful post.
      window.location.assign(`/photo/${this.state.photoId}`);
    });
  }

  render() {
    let notSelected = {
      margin: "0 auto",
      float: "none",
      marginBottom: "10px"
    };

    let selectedTag = {
      margin: "0 auto",
      float: "none",
      marginBottom: "10px",
      backgroundColor: "#dc3545",
      color: "white"
    };

    if (this.state.isLoaded) {
      const tagData = this.state.tags;

      const tag = tagData.map((tag, index) => {
        const tagName = tag["tag_name"];
        const humanTag = tag["human_readable_tag"];
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
              {humanTag}
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
                Tags for this photo{" "}
                <span className="font-weight-bold font-italic">
                  {" "}
                  {this.state.title}{" "}
                </span>
              </h3>
              <p class="text-left">
                Tags for this photo are shown below. Select the tags you want to
                remove by clicking on them.
              </p>
              <hr />
              {tag}
            </div>
          </div>
          <hr />
          <div className="row">
            <div className="col text-center">
              <button
                className="btn btn-success btn-block btn-lg"
                onClick={() => this.backToPhoto()}
              >
                Return to photo
              </button>
            </div>

            <div className="col text-center">
              <button
                className="btn btn-danger btn-block btn-lg"
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
            <h2>There was a problem getting data.</h2>
          </div>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#tag-selector");
ReactDOM.render(e(TagSelector), domContainer);
