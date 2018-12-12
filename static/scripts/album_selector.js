"use strict";

const e = React.createElement;

class AlbumSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      albums: null,
      currentOffset: 20,
      selectedAlbum: [],
      albumId: null
    };

    this.albumClick = this.albumClick.bind(this);
  }

  componentWillMount() {
    console.log("hello from componentWillMount");
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("/");
    const albumId = splitUrl[5];

    fetch("http://127.0.0.1:5000/api/getalbums")
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
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getNextAlbums() {
    console.log("next called ", this.state.currentOffset);

    fetch(
      `http://127.0.0.1:5000/api/getalbums?offset=${this.state.currentOffset +
        20}`
    )
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
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getPreviousAlbums() {
    console.log("previous called ", this.state.currentOffset);

    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(
      `http://127.0.0.1:5000/api/getalbums?offset=${this.state.currentOffset -
        20}`
    )
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
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  sendData() {
    console.log("getting here?", this.state.albumId, this.state.selectedAlbum);
    fetch("http://127.0.0.1:5000/api/getalbums", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.albumId,
        albums: this.state.selectedAlbum
      })
    }).then(() => {
      // redirect after successful post
      window.location.assign(
        `http://127.0.0.1:5000/albums/${this.state.albumId}`
      );
    });
  }

  albumClick(album_id) {
    console.log("Greetings from albumClick the album_id is ", album_id);

    let tempArray = [];
    tempArray.push(album_id);

    // i only wan this to allow one item in the array
    this.setState({
      selectedAlbum: tempArray
    });

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
      backgroundColor: "#28a745"
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
      let test = Object.keys(albums).map(function(key, index) {
        return (
          <div key={albums[key]["album_id"]} className="col text-right">
            <div
              id="photo-select"
              className="card"
              // not ideal right here...but it works
              onClick={function(event) {
                albumClick(albums[key]["album_id"]);
              }}
              style={
                selectedAlbum.includes(albums[key]["album_id"])
                  ? selectedCard
                  : cardStyle
              }
            >
              <div className="card-header">
                <h5 className="card-title text-center">
                  {" "}
                  {albums[key]["title"]}{" "}
                </h5>{" "}
              </div>
              <div className="card-body">
                <img
                  src={albums[key]["large_square"]}
                  alt="Responsive image"
                  className="card-img-top"
                />
              </div>{" "}
            </div>{" "}
          </div>
        );
      });

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getPreviousAlbums()}
              >
                Next{" "}
              </button>{" "}
            </div>{" "}
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getNextAlbums()}
              >
                Previous{" "}
              </button>{" "}
            </div>{" "}
          </div>
          <hr />
          <div className="row"> {test} </div>
          <div className="row">
            <div className="col text-left">
              <a href="/edit/albums">
                <button className="btn btn-success btn-lg">
                  Return to edit albums without making changes{" "}
                </button>{" "}
              </a>{" "}
            </div>
            <div className="col text-right">
              <button
                type="submit"
                className="btn btn-warning btn-lg"
                onClick={() => this.sendData()}
              >
                Add photos{" "}
              </button>{" "}
            </div>
          </div>
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

const domContainer = document.querySelector("#album-selector");
ReactDOM.render(e(AlbumSelector), domContainer);