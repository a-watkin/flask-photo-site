"use strict";

const e = React.createElement;

class PhotosData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20,
      selectedPhotos: [],
      albumId: null
    };

    // this.photoClick = this.photoClick.bind(this);
  }

  componentWillMount() {
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("/");
    const albumId = splitUrl[5];

    fetch("http://127.0.0.1:5000/api/uploaded")
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos
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
    console.log("getting here?", this.state.albumId, this.state.selectedPhotos);
    // /api/getphotos
    fetch("http://127.0.0.1:5000/api/getphotos", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.albumId,
        photos: this.state.selectedPhotos
      })
    }).then(() => {
      // redirect after successful post
      window.location.assign(
        `http://127.0.0.1:5000/albums/${this.state.albumId}`
      );
    });
  }

  render() {
    let photo = null;
    if (this.state.items) {
      let photos = this.state.items;
      console.log(photos);
      let photo = Object.keys(photos).map(function(key, index) {
        let photo_url = photos[key]["original"];
        console.log(photo_url);
        return (
          <div>
            <hr />
            <div key={photos[key]["photo_id"]} className="row">
              <div className="col">
                <img
                  src={photos[key]["original"]}
                  alt="Uploaded photo"
                  className="img-fluid"
                />
              </div>
              <div className="col text-center">
                <h5>Where title will go</h5>
                <h6>{photos[key]["photo_id"]}</h6>
              </div>
            </div>
          </div>
        );
      });

      return (
        <div>
          <h1> Hi form other React </h1> {photo}
        </div>
      );
    }

    return (
      <div>
        <h1>Hi from React</h1>

        {photo}
      </div>
    );
  }
}

const domContainer = document.querySelector("#upload-editor");
ReactDOM.render(e(PhotosData), domContainer);
