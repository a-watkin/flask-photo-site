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
    // Getting the album id from the URL.
    let currentUrl = window.location.href;

    fetch("/photo/album/api/getalbums", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(
        result => {
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

  getNextAlbums() {
    fetch(
      `/photo/album/api/getalbums?offset=${this.state.currentOffset + 20}`,
      {
        credentials: "include"
      }
    )
      .then(res => res.json())
      .then(
        result => {
          if (Object.keys(result["albums"]).length === 0) {
            return false;
          }

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

  getPreviousAlbums() {
    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(
      `/photo/album/api/getalbums?offset=${this.state.currentOffset - 20}`,
      {
        credentials: "include"
      }
    )
      .then(res => res.json())
      .then(
        result => {
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
    // Guards against sending data if no album is selected.
    if (this.state.selectedAlbum.length < 1) {
      return false;
    }

    fetch("/photo/album/api/getalbums", {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.selectedAlbum
      })
    })
      .catch(error => console.error(error))
      .then(() => {
        window.location.assign(`/photo/album/${this.state.selectedAlbum[0]}`);
      });
  }

  albumClick(album_id) {
    if (
      this.state.selectedAlbum.length === 1 &&
      this.state.selectedAlbum[0] === album_id
    ) {
      let tempArray = [...this.state.selectedAlbum];
      tempArray.splice(0, 1);
      this.setState({
        selectedAlbum: tempArray
      });
    } else {
      let tempArray = [];
      tempArray.push(album_id);

      // I only want this to allow one item in the array.
      this.setState({
        selectedAlbum: tempArray
      });
    }

    // Not ideal but good enough for now.
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

    let albumClick = this.albumClick;

    if (this.state.albums) {
      large_square = this.state.albums[0]["large_square"];
      const albums = this.state.albums;

      let test = Object.keys(albums).map(function(key) {
        return (
          <div key={albums[key]["album_id"]} className="col text-right">
            <div
              id="photo-select"
              className="card"
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
                  <a
                    id="album-links"
                    href={`/photo/album/${albums[key]["album_id"]}`}
                  >
                    {albums[key]["human_readable_title"]}{" "}
                  </a>
                </h5>{" "}
              </div>
              <div className="card-body">
                <img
                  src={albums[key]["large_square"]}
                  alt="Responsive image"
                  className="card-img-top img-fluid"
                />
                <p className="card-text text-left">
                  {albums[key]["human_readable_description"]}{" "}
                </p>
              </div>{" "}
              <div className="row">
                <div className="col text-center">
                  <p>views: {albums[key]["views"]}</p>
                </div>

                <div className="col text-center">
                  <p> photos: {albums[key]["photos"]} </p>{" "}
                </div>
              </div>
              <div className="col" />
            </div>{" "}
          </div>
        );
      });

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getPreviousAlbums()}
              >
                Newer{" "}
              </button>{" "}
            </div>{" "}
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getNextAlbums()}
              >
                Older{" "}
              </button>{" "}
            </div>{" "}
          </div>
          <hr />
          <div className="row"> {test} </div>
          <hr />
          <div className="row">
            <div className="col text-left">
              <a href="/photo/upload/uploaded">
                <button className="btn btn-success btn-block btn-lg">
                  Return to uploaded photos{" "}
                </button>{" "}
              </a>{" "}
            </div>
            <div className="col text-right">
              <button
                type="submit"
                className="btn btn-warning btn-block btn-lg"
                onClick={() => this.sendData()}
              >
                Save to album{" "}
              </button>{" "}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col">
          <h2> There was a problem getting data. </h2>
        </div>{" "}
      </div>
    );
  }
}

const domContainer = document.querySelector("#album-selector");
ReactDOM.render(e(AlbumSelector), domContainer);
