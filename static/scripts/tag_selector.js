"use strict";

const e = React.createElement;

class TagSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      photoData: null,
      selectedTags: [],
      albumId: null
    };

    this.tagClick = this.tagClick.bind(this);
  }

  componentWillMount() {
    console.log("hello from componentWillMount");
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("=");
    let albumId = splitUrl[1];

    fetch(`/api/get/phototags?photo_id=${albumId}`)
      .then(res => res.json())
      .then(
        result => {
          // ok i am getting the data
          console.log(`result ${result}`, Object.keys(result), result.original);
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

  sendData() {
    if (this.state.selectedAlbum.length < 1) {
      console.log("do nothing if no album has been selected");
      return false;
    }

    console.log("getting here?", this.state.selectedAlbum);
    fetch("http://127.0.0.1:5000/api/getalbums", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.selectedAlbum
      })
    }).then(() => {
      console.log("eh");
      // redirect after successful post
      window.location.assign(
        `http://127.0.0.1:5000/albums/${this.state.selectedAlbum[0]}`
      );
    });
  }

  tagClick(album_id) {
    console.log("Greetings from albumClick the album_id is ", album_id);
    console.log(this.state.selectedAlbum);

    if (
      this.state.selectedAlbum.length === 1 &&
      this.state.selectedAlbum[0] === album_id
    ) {
      console.log("deselect it?");
      let tempArray = [...this.state.selectedAlbum];
      tempArray.splice(0, 1);
      console.log(tempArray);
      this.setState({
        selectedAlbum: tempArray
      });

      console.log(this.state.selectedAlbum);
    } else {
      let tempArray = [];
      tempArray.push(album_id);

      // i only wan this to allow one item in the array
      this.setState({
        selectedAlbum: tempArray
      });
    }

    // also not ideal but good enough for now
    this.forceUpdate();
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

    if (this.state.isLoaded) {
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
