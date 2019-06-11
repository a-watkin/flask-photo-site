"use strict";

const e = React.createElement;

class SelectPhotos extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20,
      selectedPhotos: [],
      albumId: null,
      photoLimit: null
    };

    this.photoClick = this.photoClick.bind(this);
  }

  componentWillMount() {
    // Getting the album id from the URL.
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("/");
    const albumId = splitUrl[6];

    fetch(`/photo/album/api/albumphotos?album_id=${albumId}`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(
        result => {
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset,
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

  getNextPhotos() {
    const albumId = this.state.albumId;

    // I had a problem here with the number being treated as a string
    // so to safe guard against coercion.
    let currentOffset = Number(this.state.currentOffset);
    fetch(
      `/photo/album/api/albumphotos?album_id=${albumId}&offset=${currentOffset +
        20}`,
      {
        credentials: "include"
      }
    )
      .then(res => res.json())
      .then(
        result => {
          if ((result.photos, Object.keys(result.photos).length > 0)) {
            this.setState({
              isLoaded: true,
              items: result.photos,
              currentOffset: result.offset
            });
          }
        },
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getPreviousPhotos() {
    const albumId = this.state.albumId;

    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(
      `/photo/album/api/albumphotos?album_id=${albumId}&offset=${this.state
        .currentOffset - 20}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      }
    )
      .then(result => result.json())
      .then(result => {
        this.setState({
          isLoaded: true,
          items: result.photos,
          currentOffset: result.offset
        });
      })
      .catch(error => console.error(error))
      .then(() => {
        this.setState({
          isLoaded: true,
          error
        });
      });
  }

  sendData() {
    fetch(`/photo/album/edit/${this.state.albumId}/remove/photos`, {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.albumId,
        photos: this.state.selectedPhotos
      })
    })
      .catch(error => console.error(error))
      .then(() => {
        // Redirect after successful post.
        window.location.assign(`/photo/album/${this.state.albumId}`);
      });
  }

  photoClick(photo_id) {
    if (!this.state.selectedPhotos.includes(photo_id)) {
      this.state.selectedPhotos.push(photo_id);
    } else {
      // Remove the photo from the array.
      let tempAray = [...this.state.selectedPhotos];
      let index = tempAray.indexOf(photo_id);
      if (index !== -1) {
        tempAray.splice(index, 1);
        this.setState({
          selectedPhotos: tempAray
        });
      }
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
      backgroundColor: "#dc3545"
    };

    let selectedPhotos = this.state.selectedPhotos;
    let large_square = "";
    let photoClick = this.photoClick;

    console.log(this.state.items);

    if (this.state.items) {
      large_square = this.state.items[0]["large_square"];
      const photos = this.state.items;

      let test = Object.keys(photos).map(function(key, index) {
        return (
          <div key={photos[key]["photo_id"]} className="col text-right">
            <div
              id="photo-select"
              className="card"
              onClick={function(event) {
                photoClick(photos[key]["photo_id"]);
              }}
              style={
                selectedPhotos.includes(photos[key]["photo_id"])
                  ? selectedCard
                  : cardStyle
              }
            >
              <div className="card-header">
                <h5 className="card-title text-center">
                  {photos[key]["human_readable_title"]}
                </h5>
              </div>

              <div className="card-body">
                <img
                  src={photos[key]["large_square"]}
                  alt="Responsive image"
                  className="card-img-top img-fluid"
                />
              </div>
            </div>
          </div>
        );
      });

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getPreviousPhotos()}
              >
                Newer
              </button>
            </div>
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getNextPhotos()}
              >
                Older
              </button>
            </div>
          </div>

          <hr />

          <div className="row"> {test} </div>

          <div className="row">
            <div className="col text-left">
              <a href="/photo/album/edit/albums">
                <button className="btn btn-success btn-block btn-lg">
                  Return to edit albums
                </button>
              </a>
            </div>

            <div className="col text-right">
              <button
                type="submit"
                className="btn btn-warning btn-block btn-lg"
                onClick={() => this.sendData()}
              >
                Remove photos
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col">
          <h2> There was a problem getting data. </h2>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#photos-selector");
ReactDOM.render(e(SelectPhotos), domContainer);
