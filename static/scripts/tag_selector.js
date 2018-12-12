"use strict";

const e = React.createElement;

class TagSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      selectedTags: [],
      albumId: null
    };

    this.albumClick = this.albumClick.bind(this);
  }

  componentWillMount() {
    console.log("hello from componentWillMount");
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("=");
    const albumId = splitUrl[1];

    fetch(`http://127.0.0.1:5000/api/get/phototags?photo_id=${albumId}`)
      .then(res => res.json())
      .then(
        result => {
          console.log("result", result);
          this.setState({
            isLoaded: true,
            albums: result.albums,
            currentOffset: result.offset
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

  albumClick(album_id) {
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

    let selectedCard = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px",
      backgroundColor: "#28a745",
      color: "white"
    };

    let selectedAlbum = this.state.selectedAlbum;
    let large_square = "";
    // it doesn't seemt to be able to get this reference
    // without delaring it here from the Objct.keys reurn statment
    // also passing it and invoking leads to it being executed twice?
    let albumClick = this.albumClick;

    if (this.state.albums) {
      large_square = this.state.albums[0]["large_square"];
      const albums = this.state.albums;

      // console.log(this.state.items[0]["large_square"]);
      let test = Object.keys(albums).map(function(key) {
        return (
          <div className="col text-right">
            <h1>Tag selector </h1>
          </div>
        );
      });

      return (
        <div>
          <h1>hello from tag selector </h1>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col">
          <h1> Some problem with getting the data. </h1>{" "}
        </div>{" "}
      </div>
    );
  }
}

const domContainer = document.querySelector("#tag-selector");
ReactDOM.render(e(TagSelector), domContainer);
